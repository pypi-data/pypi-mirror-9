"""
    distutilazy.tests.test_clean
    ----------------------------

    Tests for distutilazy.clean module

    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import

import sys
import os
from os import path
import shutil
import unittest

from .setup_test_env import TEST_DIR
from distutilazy import clean
from distutils.dist import Distribution

class TestClean(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_cache_dir = path.join(TEST_DIR, '_test_py_cache_')
        if path.exists(cls.test_cache_dir):
            raise Exception(
                    "Test python cache directory exsits in {0}. Please remove this path".format(
                        cls.test_cache_dir
                        )
                    )
        else:
            os.mkdir(cls.test_cache_dir)

    @classmethod
    def tearDownAfter(cls):
        if path.exists(cls.test_cache_dir):
            shutil.rmtree(cls.test_cache_dir, True)

    def test_clean_all(self):
        dist = Distribution()
        dist.metadata.name = "testdist"
        cl = clean.clean_all(dist)
        cl.finalize_options()
        self.assertEqual(cl.get_egginfo_dir(), "testdist.egg-info")
        targets = ["build", "dist", "egginfo", "extra"]
        bad_calls = []
        good_calls = []
        good_calls_should_be = 0
        for target in targets:
            cl = clean.clean_all(dist)
            cl.finalize_options()
            cl.dry_run = True
            setattr(cl, "keep_%s" % target, True)
            setattr(cl, "clean_%s" % target, lambda self: bad_calls.append(targt))
            other_targets = [t for t in targets if t != target]
            for ot in other_targets:
                good_calls_should_be += 1
                setattr(cl, "clean_%s" % ot, lambda self=None: good_calls.append(ot))
            cl.run()
        self.assertEqual(bad_calls, [])
        self.assertEqual(len(good_calls), good_calls_should_be)

    def test_clean_pyc(self):
        dist = Distribution()
        cl = clean.clean_pyc(dist)
        cl.extensions = "ppyycc, ppyyoo"
        cl.finalize_options()
        self.assertEqual(cl.extensions, ["ppyycc", "ppyyoo"])
        self.assertEqual(cl.find_compiled_files(), [])

    def test_clean_py_cache_dirs(self):
        dist = Distribution()
        cl = clean.clean_pyc(dist)
        cl.directories = "_test_py_cache_"
        cl.finalize_options()
        self.assertEqual(cl.directories, ["_test_py_cache_"])
        self.assertEqual(cl.find_cache_directories(), [self.__class__.test_cache_dir])
        cl.run()
        self.assertFalse(path.exists(self.__class__.test_cache_dir))

    def test_clean_py_cache_dirs_finds_nothing(self):
        dist = Distribution()
        cl = clean.clean_pyc(dist)
        cl.extensions = "ppyycc, ppyyoo"
        cl.directories = "not_exist, and_not_found"
        cl.finalize_options()
        self.assertEqual(cl.directories, ["not_exist", "and_not_found"])
        self.assertEqual(cl.find_cache_directories(), [])
