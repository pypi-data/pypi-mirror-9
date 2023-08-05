"""
    distutilazy.tests
    -----------------

    Tests for distutilazy

    :license: MIT, see LICENSE for more details.
"""

from os import path
import glob

test_modules = [path.splitext(path.basename(filename))[0] for filename in glob.glob(path.join(path.dirname(__file__), 'test*.py'))]
test_modules.sort()
__all__ = test_modules
