"""

    distutilazy.clean
    -----------------

    command classes to help clean temporary files

    :license: MIT, see LICENSE for more details.

"""

from __future__ import absolute_import

import os
import shutil
from distutils import log
from distutils.core import Command
from distutils.command import clean

from . import util

__version__ = "0.4.0"

class clean_pyc(Command):
    description = """Clean root dir from complied python files"""
    user_options = [("root=", "r", "path to root dir")]

    def initialize_options(self):
        self.root = os.getcwd()
        self.extensions = "pyc,pyo,pyd"
        self.directories = "__pycache__,"

    def finalize_options(self):
        if not os.path.exists(self.root):
            raise IOError("Failed to access root path " + self.root)
        self.extensions = [ext.strip() for ext in self.extensions.split(',')]
        self.directories = [dirname.strip() for dirname in self.directories.split(',')]

    def find_compiled_files(self):
        """Find compiled Python files recursively in the root path

        :return: list of absolute file paths
        """
        files = []
        for ext in self.extensions:
            extfiles = util.find_files(self.root, "*." + ext)
            log.debug("found {0} .{1} files in {2}".format(len(extfiles), ext, self.root))
            files.extend(extfiles)
            del extfiles
        self.announce("found {0} compiled python files in {1}".format(len(files), self.root))
        return files

    def find_cache_directories(self):
        directories = []
        for dirname in self.directories:
            dirs = util.find_directories(self.root, dirname)
            log.debug("found {0} directories in {1}".format(len(dirs), self.root))
            directories.extend(dirs)
            del dirs
        self.announce("found {0} python cache directories in {1}".format(len(directories), self.root))
        return directories

    def _clean_file(self, filename):
        """Clean a file if exists"""
        if not os.path.exists(filename):
            return
        self.announce("removing " + filename)
        if not self.dry_run:
            os.remove(filename)

    def _clean_directory(self, dirname):
        """Clean a directory if exists"""
        if not os.path.exists(dirname):
            return
        self.announce("removing directory {0} and all it's contents".format(dirname))
        if not self.dry_run:
            shutil.rmtree(dirname, True)

    def run(self):
        dirs = self.find_cache_directories()
        if dirs:
            self.announce("cleaning python cache directories in {0} ...".format(self.root))
            if not self.dry_run:
                for dirname in dirs:
                    self._clean_directory(dirname)

        files = self.find_compiled_files()
        if files:
            self.announce("cleaning compiled python files in {0} ...".format(self.root))
            if not self.dry_run:
                for filename in files:
                    self._clean_file(filename)

class clean_all(clean.clean, clean_pyc):
    description = """Clean root dir from temporary files, complied files, etc."""
    user_options = [
        ("keep-build", None, "do not clean build direcotry"),
        ("keep-dist", None, "do not clean dist direcotry"),
        ("keep-egginfo", None, "do not clean egg info direcotry"),
        ("keep-extra", None, "do not clean extra files"),
    ]

    boolean_options = ["keep-build", "keep-dist", "keep-egginfo", "keep-extra"]

    def initialize_options(self):
        clean.clean.initialize_options(self)
        clean_pyc.initialize_options(self)
        self.keep_build = None
        self.keep_dist = None
        self.keep_egginfo = None
        self.keep_extra = None

    def finalize_options(self):
        clean.clean.finalize_options(self)
        clean_pyc.finalize_options(self)
        self.all = True

    def get_egginfo_dir(self):
        return self.distribution.metadata.get_name() + ".egg-info"

    def get_extra_paths(self):
        """Return list of extra files/directories to be removed"""
        return []

    def clean_egginfo(self):
        """Clean .egginfo directory"""
        dirname = os.path.join(self.root, self.get_egginfo_dir())
        self._clean_directory(dirname)

    def clean_dist(self):
        self._clean_directory(os.path.join(self.root, "dist"))

    def clean_build(self):
        self._clean_directory(os.path.join(self.root, "build"))

    def clean_extra(self):
        """Clean extra files/directories specified by get_extra_paths()"""
        extra_paths = self.get_extra_paths()
        for path in extra_paths:
            if not os.path.exists(path):
                continue
            if os.path.isdir(path):
                self._clean_directory(path)
            else:
                self._clean_file(path)

    def run(self):
        clean.clean.run(self)
        clean_pyc.run(self)
        if not self.keep_build:
            self.clean_build()
        if not self.keep_egginfo:
            self.clean_egginfo()
        if not self.keep_dist:
            self.clean_dist()
        if not self.keep_extra:
            self.clean_extra()
