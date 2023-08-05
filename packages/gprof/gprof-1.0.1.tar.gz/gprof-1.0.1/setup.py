import os
from setuptools import setup, find_packages

here = os.path.dirname(os.path.abspath(__file__))

setup(
    name='gprof',
    version='1.0.1',
    author="Sergey Kirillov",
    author_email="sergey.kirillov@gmail.com",
    description="Greenlet profiler. Measures CPU time (instead of wall time) and designed specially for greenlets.",
    packages=find_packages('.'),
    install_requires=[
    ],
    url='https://bitbucket.org/rushman/gprof',
    long_description=open(os.path.join(here, 'README.rst'), 'rb').read().decode('utf-8')
)
