"""
    distutilazy.tests.test_pyinstaller
    ----------------------------------

    Tests for distutilazy.pyinstaller module.

    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import

import sys
import os
import unittest
import re

from .setup_test_env import *
from distutilazy import pyinstaller
from distutils.dist import Distribution

class TestPyinstaller(unittest.TestCase):

    def test_finalize_opts(self):
        dist = Distribution()
        pi = pyinstaller.bdist_pyinstaller(dist)
        pi.target = "fake.py"
        pi.finalize_options()
        self.assertTrue( re.match(".+", pi.name) )
        self.assertTrue(pi.pyinstaller_opts)

    def test_clean_all(self):
        dist = Distribution()
        cl = pyinstaller.clean_all(dist)
        cl.finalize_options()
        paths = cl.get_extra_paths()
        self.assertTrue(paths)
        spec = paths.pop()
        self.assertTrue( re.match("\S+\.spec", spec) )
