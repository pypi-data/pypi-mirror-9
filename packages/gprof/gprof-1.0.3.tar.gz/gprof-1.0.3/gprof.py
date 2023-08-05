import sys
import greenlet
import gevent
import gc
import inspect
from collections import defaultdict, Counter

import resource


def clock_gettime_cpu():
    r = resource.getrusage(resource.RUSAGE_SELF)
    return r.ru_utime + r.ru_stime

# import ctypes, os

# import cffi

# CDEFS = """
# double clock_gettime_cpu();
# """

# CSRC = """
# #include <time.h>


# double
# clock_gettime_cpu()
# {
#     struct timespec         ts;
#     double                  result;

#     if ((clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &ts)) < 0) {
#         perror("clock_gettime");
#         exit(1);
#     }

#     result = ts.tv_sec + ts.tv_nsec * pow(10, -9);
#     return (result);
# }
# """

# ffi = cffi.FFI()
# ffi.cdef(CDEFS)
# our_lib = ffi.verify(CSRC)

# clock_gettime_cpu = our_lib.clock_gettime_cpu
# process_cpu_time = clock_gettime_cpu

#from trace import Trace

class FuncTime(object):
    def __init__(self, func, start_time):
        self.func = func
        self.start_time = start_time
        self.own_time = 0.0
        self.cum_time = 0.0

    def time(self, now):
        return now - self.start_time

    def record_start(self, now):
        self.start_time = now

    def record_own(self, now):
        self.own_time += self.time(now)

    def record_cum(self, now):
        self.cum_time += self.time(now)


class GProfiler(object):
    def __init__(self, clock=clock_gettime_cpu):
        self.clock = clock
        self.stats = defaultdict(lambda: {'cum_times':0.0, 'own_times': 0.0, 'n_calls': 0, 'callers': Counter()})
        self.per_greenlet_stack = defaultdict(list)
        self._last_switch_time = None
        self._code_class_cache = {}

    def start(self):
        greenlet.settrace(self.greenlet_trace)
        sys.setprofile(self.python_global_trace)

    def stop(self):
        greenlet.settrace(None)
        sys.setprofile(None)

    def greenlet_trace(self, action, (origin, target)):
        gevent_hub = gevent.hub.get_hub()

        if origin is not gevent_hub:
            # record execution time
            if self.per_greenlet_stack[origin]:
                last_func_time = self.per_greenlet_stack[origin][-1]
                self.stats[last_func_time.func].record_own(self.clock())

        if target is not gevent_hub:
            # record start time
            if self.per_greenlet_stack[target]:
                last_func_time = self.per_greenlet_stack[target][-1]
                last_func_time.record_start(self.clock())

    def python_global_trace(self, frame, event, arg):
        func = self.get_func_info(frame)

        func_stats = self.stats[func]
        #print event, func, arg
        if event == 'call':
            if frame.f_back:
                func_stats['callers'][self.get_func_info(frame.f_back)] += 1
            func_stats['n_calls'] += 1
            self.push_stack(func)

        elif event == 'return':
            self.pop_stack(func)

        elif event.startswith('c_'):
            c_func_stats = self.stats[self.get_cfunc_info(arg)]
            if event == 'c_call':
                if frame.f_back:
                    c_func_stats['callers'][func] += 1
                self.push_stack(self.get_cfunc_info(arg))
                c_func_stats['n_calls'] += 1
            elif event == 'c_return':
                self.pop_stack(self.get_cfunc_info(arg))
            elif event == 'c_exception':
                self.pop_stack(self.get_cfunc_info(arg))

    def push_stack(self, func):
        stack = self.per_greenlet_stack[gevent.getcurrent()]
        now = self.clock()

        # record time spent in this function
        if stack:
            prev_time = stack[-1]
            prev_time.record_own(now)

        # push new function to stack
        stack.append(FuncTime(func, now))
        #print "pushing into {0}".format(func)

    def pop_stack(self, func):
        stack = self.per_greenlet_stack[gevent.getcurrent()]
        if not stack:
            return
        func_time = stack.pop()
        assert func_time.func == func, '{0!r} != {1!r}'.format(func_time.func, func)

        now = self.clock()
        func_time.record_own(now)

        # # record execution time as now - function start time
        func_stats = self.stats[func_time.func]
        func_stats['own_times'] = func_time.own_time
        func_stats['cum_times'] = func_time.cum_time + func_time.own_time

        #print "popping {0} adding {1} to own and {2}+{3} to cum".format(func_time.func, func_time.own_time, func_time.cum_time, func_time.own_time)

        if stack:
            prev_time = stack[-1]
            prev_time.cum_time += func_time.cum_time + func_time.own_time
            prev_time.record_start(now)
            #print "returning to {0} from {1} adding {2} to cumtime".format(prev_time.func, func_time.func, func_time.cum_time + func_time.own_time)

    def get_class_name(self, code):
        if code in self._code_class_cache:
            if self._code_class_cache[code] is not None:
                return self._code_class_cache[code]
        else:
            self._code_class_cache[code] = None
            funcs = [f for f in gc.get_referrers(code) if inspect.isfunction(f)]
            if len(funcs) == 1:
                dicts = [d for d in gc.get_referrers(funcs[0]) if isinstance(d, dict)]
                if len(dicts) == 1:
                    classes = [c for c in gc.get_referrers(dicts[0]) if hasattr(c, '__bases__')]
                    if len(classes) == 1:
                        clsname = classes[0].__name__
                        self._code_class_cache[code] = clsname
                        return clsname

    def get_func_info(self, frame):
        code = frame.f_code
        clsname = self.get_class_name(code)
        if clsname:
            funcname = '{0}.{1}'.format(clsname, code.co_name)
        else:
            funcname = code.co_name
        return (code.co_filename, code.co_firstlineno, funcname)

    def get_cfunc_info(self, cfunc):
        s = cfunc.__self__
        str_name = '{0}.{1}'.format(type(s).__name__, cfunc.__name__) if s is not None else cfunc.__name__

        return ("", 0, str_name)

    def save(self, filename):
        import marshal

        pstats = {}
        for func, data in self.stats.items():
            pstats[func] = [data['n_calls'], data['n_calls'], data['own_times'], data['cum_times'], dict(data['callers'])]

        with open(filename, 'wb') as f:
            marshal.dump(pstats, f)


if __name__ == '__main__':
    import time
    def double_inner_func():
        for i in xrange(10000000):
            1*2
        pass

    def sleepfunc():
        time.sleep(1)

    def inner_func():
        #for i in xrange(10000000):
        #    1*5
        sleepfunc()
        return double_inner_func()

    def func():
        return inner_func()

    p = GProfiler()
    p.start()
    func()
    p.stop()
    #p.save('profile')
    for key, val in sorted(p.stats.iteritems(), key=lambda x: x[1]['cum_times'], reverse=True):
        print key, val['own_times'], val['cum_times']