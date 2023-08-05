"""

    distutilazy.test
    -----------------

    command classes to help run tests

    :license: MIT, see LICENSE for more details.

"""

from __future__ import absolute_import

import os
import sys
import glob
import importlib
import unittest
from distutils.core import Command

__version__ = "0.1.0"

class run_tests(Command):
    description = """Run test suite"""
    user_options = [("root=", "r", "path to tests suite dir"),
                    ("pattern=", "p", "test file name pattern"),
                    ("verbosity=", "v", "verbosity level [1,2,3]"),
                    ("files=", None, "run specified test files (comma separated)")]

    def initialize_options(self):
        self.root = os.path.join(os.getcwd(), 'tests')
        self.pattern = "test*.py"
        self.verbosity = 1
        self.files = None

    def finalize_options(self):
        if not os.path.exists(self.root):
            raise IOError("Failed to access root path " + self.root)
        verbosity = min(int(self.verbosity), 3)
        if verbosity < 1:
            self.verbosity = 1
        else:
            self.verbosity = verbosity
        if self.files:
            self.files = map(lambda name: name.strip(), self.files.split(','))

    def get_modules_from_files(self, files):
        modules = []
        for filename in files:
            dirname = os.path.dirname(filename)
            package_name = os.path.basename(dirname)
            if package_name:
                try:
                    self.announce("importing {0} as package ...".format(package_name))
                    package = importlib.import_module(package_name)
                    if hasattr(package, '__path__') and os.path.abspath(package.__path__[0]) != os.path.abspath(dirname):
                        raise ImportError("directory {1} is not a package to import".format(dirname))
                except ImportError as err:
                    self.announce("failed to import {0}. not a package. {1}".format(package_name, err))
                    sys.path.insert(0, dirname)
                    package_name = None
            modulename, _, extension = os.path.basename(filename).rpartition('.')
            if not modulename:
                self.announce("failed to find module name from filename '{0}'. skipping this file".format(filename))
                continue
            if package_name:
                modulename = '.' + modulename
            self.announce("importing module {0} from file {1} ...".format(modulename, filename))
            module = importlib.import_module(modulename, package=package_name)
            modules.append(module)
        return modules

    def find_test_modules_from_package_path(self, package_path):
        """Check if the path is a package, and if it introduces modules"""
        package_dir = os.path.dirname(package_path)
        package_name = os.path.basename(package_path)
        if package_dir:
            sys.path.insert(0, package_dir)
        try:
            package = importlib.import_module(package_name)
            if package and hasattr(package, '__all__'):
                modules = []
                for module_name in package.__all__:
                    module = importlib.import_module('{0}.{1}'.format(package_name, module_name))
                    modules.append(module)
                return modules
        except ImportError as exp:
            pass
        return []

    def find_test_modules_from_test_files(self, root, pattern):
        """Return list of test modules from the path whose filename matches the pattern"""
        test_files = glob.glob(os.path.join(root, pattern))
        if not test_files:
            return []
        package_name = os.path.basename(root)
        try:
            self.announce("importing {0} as package ...".format(package_name))
            package = importlib.import_module(package_name)
            if hasattr(package, '__path__') and os.path.abspath(package.__path__[0]) != os.path.abspath(root):
                raise ImportError("directory {1} is not a package to import".format(root))
        except ImportError as err:
            self.announce("failed to import {0}. not a package. {1}".format(package_name, err))
            sys.path.insert(0, root)
            package_name = None
        modules = []
        for filename in test_files:
            modulename, _, extension = os.path.basename(filename).rpartition('.')
            if not modulename:
                self.announce("failed to find module name from filename '{0}'. skipping this test".format(filename))
                continue
            if package_name:
                modulename = '.' + modulename
            self.announce("importing module {0} from file {1} ...".format(modulename, filename))
            module = importlib.import_module(modulename, package=package_name)
            modules.append(module)
        return modules

    def test_suite_for_modules(self, modules):
        suite = unittest.TestSuite()
        testLoader = unittest.defaultTestLoader
        for module in modules:
            module_tests = testLoader.loadTestsFromModule(module)
            suite.addTests(module_tests)
        return suite

    def get_test_runner(self):
        return unittest.TextTestRunner(verbosity=self.verbosity)

    def run(self):
        modules = None
        if self.files:
            modules = self.get_modules_from_files(self.files)
        else:
            self.announce("searching for test package modules ...")
            modules = self.find_test_modules_from_package_path(self.root)
            if not modules:
                self.announce("searching for test files ...")
                modules = self.find_test_modules_from_test_files(self.root, self.pattern)
        if not modules:
            self.announce("found no test files")
            return False
        suite = self.test_suite_for_modules(modules)
        runner = self.get_test_runner()
        self.announce("running tests ...")
        runner.run(suite)
