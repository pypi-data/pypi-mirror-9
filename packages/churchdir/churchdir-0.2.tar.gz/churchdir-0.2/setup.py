#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  6 19:44:34 2015

@author: kcarlton
"""

import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "churchdir",
    version = "0.2",
    description='Convert an address book from csv format to a web page.',
    author = "Ken Carlton",
    author_email = "kcarlton@c-c-church.net",
    url = 'http://c-c-church.net/directory-software/',
    license = "BSD",
    keywords = "church directory address book csv",
    #url = "http://packages.python.org/an_example_pypi_project",
    platforms = ["any"],
    long_description=read('README.rst'),
    packages=['churchdir'],
    install_requires=['colorama'],
    scripts=['bin/churchdir-quickstart'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Topic :: Communications :: Email :: Address Book",
        "Topic :: Religion",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)

