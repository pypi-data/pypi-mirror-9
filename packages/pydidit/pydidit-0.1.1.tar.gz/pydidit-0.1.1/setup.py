#!/usr/bin/env python2.7
import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="pydidit",
    version="0.1.1",
    author="Valentine Gogichashvili",
    author_email="valgog@gmail.com",
    description=("A simple command line script to publish to iDoneThis"),
    license="Apache 2.0",
    keywords="todo idonethis",
    url="http://www.github.com/valgog/pydidit",
    py_modules=['pydidit'],
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
