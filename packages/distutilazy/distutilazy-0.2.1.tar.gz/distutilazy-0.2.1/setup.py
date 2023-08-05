#!/usr/bin/env python

"""

distutilazy
===========

Extra distutils commands.

License
-------
Distutilazy is released under the terms of `MIT license <http://opensource.org/licenses/MIT>`_.

"""

from __future__ import print_function

import os
import sys

try:
    import setuptools
    from setuptools import setup
except ImportError as exp:
    setuptools = None
    from distutils.core import setup
    if (sys.version_info[0]) < 3:
        print("using distutils. install setuptools for more options", file=sys.stderr)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import distutilazy
import distutilazy.clean
import distutilazy.test

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Archiving :: Packaging",
    "Topic :: System :: Systems Administration",
]

long_description = __doc__
with open(os.path.join(os.path.dirname(__file__), "README.rst")) as fh:
    long_description = fh.read()

params = dict(
    name = "distutilazy",
    author = "Farzad Ghanei",
    author_email = "farzad.ghanei@gmail.com",
    url = "http://github.com/farzadghanei/distutilazy/",
    packages = ["distutilazy", "distutilazy.command"],
    version = distutilazy.__version__,
    description = "Extra distutils commands",
    long_description = long_description,
    license = "MIT",
    classifiers = CLASSIFIERS,
    cmdclass = {
        "clean_pyc": distutilazy.clean.clean_pyc,
        "clean_all": distutilazy.clean.clean_all,
        "test": distutilazy.test.run_tests
        }
)

if setuptools:
    params.update(zip_safe = False)

dist = setup(**params)
