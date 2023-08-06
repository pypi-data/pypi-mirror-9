#!/usr/bin/env python2.7
import os
import inspect
from setuptools import setup

__location__ = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe())))

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(__location__, fname)).read()


def read_version(package):
    data = {}
    with open(os.path.join(package, '__init__.py'), 'r') as fd:
        exec(fd.read(), data)
    return data['__version__']

MAIN_PACKAGE = "pydidit"

setup(
    name="pydidit",
    version=read_version(MAIN_PACKAGE),
    author="Valentine Gogichashvili",
    author_email="valgog@gmail.com",
    description=("A simple command line script to publish to iDoneThis"),
    license="Apache 2.0",
    keywords="todo idonethis",
    url="http://www.github.com/valgog/pydidit",
    packages=[MAIN_PACKAGE],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Topic :: Office/Business :: Scheduling",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
    ],
    install_requires=[
        'Click',
        'requests',
        'colorama'
    ],
    entry_points='''
        [console_scripts]
        didit=pydidit.cli:cli
    ''',
)
