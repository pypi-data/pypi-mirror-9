"""
    distutilazy.tests.test_test
    ----------------------------

    Tests for distutilazy.test module

    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import

import sys
import os
from os import path
import shutil
import unittest

from .setup_test_env import TEST_DIR
from distutilazy import test
from distutils.dist import Distribution

# if running in a cached compiled python file
# assume filename as python source file.
# when tests are running together, test_clean
# removes pyc files. but .py file will be available
if __file__[-1].lower() == 'c':
    __file__ = __file__[:-1]

class TestTest(unittest.TestCase):
    def _get_module_filenames(self, modules):
        return map(lambda m: path.basename(m.__file__), modules)

    def test_find_modules_from_package_path(self):
        dist = Distribution()
        test_ = test.run_tests(dist)
        test_.finalize_options()
        here = path.dirname(__file__)
        filename = path.basename(__file__)
        modules = test_.find_test_modules_from_package_path(here)
        self.assertIn(filename, self._get_module_filenames(modules))

    def test_get_modules_from_files(self):
        dist = Distribution()
        test_ = test.run_tests(dist)
        test_.finalize_options()
        self.assertEqual([], test_.get_modules_from_files(['none_existing_file']))
        modules = test_.get_modules_from_files([__file__])
        self.assertEqual(1, len(modules))
        self.assertEqual(path.basename(__file__), path.basename(modules.pop().__file__))

    def test_find_modules_from_files(self):
        dist = Distribution()
        test_ = test.run_tests(dist)
        test_.finalize_options()
        here = path.dirname(__file__)
        filename = path.basename(__file__)
        modules = test_.find_test_modules_from_test_files(here, 'none_exiting_pattern')
        self.assertEqual([], modules)
        modules = test_.find_test_modules_from_test_files(here, filename)
        self.assertEqual(1, len(modules))
        self.assertEqual(filename, path.basename(modules.pop().__file__))
        modules = test_.find_test_modules_from_test_files(here, 'test_*')
        self.assertIn(filename, self._get_module_filenames(modules))

    def test_test_suite_for_modules(self):
        dist = Distribution()
        test_ = test.run_tests(dist)
        test_.finalize_options()
        suite = test_.test_suite_for_modules([])
        self.assertIsInstance(suite, unittest.TestSuite)

    def test_get_test_runner(self):
        dist = Distribution()
        test_ = test.run_tests(dist)
        test_.finalize_options()
        runner = test_.get_test_runner()
        self.assertTrue(hasattr(runner, 'run'))
        self.assertTrue(hasattr(runner.run, '__call__'))

