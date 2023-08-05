"""
    distutilazy.tests.test_util
    -----------------

    Test distutilazy.util module.

    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import

import os
from os import path
import sys
import unittest

from .setup_test_env import TEST_DIR
from distutilazy import util

# if running in a cached compiled python file
# assume filename as python source file.
# when tests are running together, test_clean
# removes pyc files. but .py file will be available
if __file__[-1].lower() == 'c':
    __file__ = __file__[:-1]

class TestUtil(unittest.TestCase):

    def test_util_find_files(self):
        me = os.path.realpath(__file__)
        files = util.find_files(TEST_DIR, "test_util.py*")
        self.assertTrue(me in files)
        files = util.find_files(TEST_DIR, "not_existing_file.py")
        self.assertEqual(files, [])

    def test_util_find_directories(self):
        found = util.find_directories(path.dirname(TEST_DIR), "tes*")
        self.assertTrue(TEST_DIR in found)
        found = util.find_directories(TEST_DIR, "not_existing_dir")
        self.assertEqual(found, [])
