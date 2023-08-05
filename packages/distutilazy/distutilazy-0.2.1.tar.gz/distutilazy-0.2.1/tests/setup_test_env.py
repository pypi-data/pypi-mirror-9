"""

    distutilazy.tests.setup_test_env
    -----------------

    Sets up the test environment and provides methods to access the test data

    :license: MIT, see LICENSE for more details.

"""

import os
import sys

__version__ = "0.1.0"
__all__ = ['setupenv', 'TEST_DIR']

TEST_DIR = os.path.realpath(os.path.dirname(__file__))

def setupenv():
    try:
        sys.path.index(TEST_DIR)
    except ValueError:
        sys.path.insert(0, TEST_DIR)
    base_path = os.path.realpath(os.path.join(TEST_DIR, '..'))
    try:
        sys.path.index(base_path)
    except ValueError:
        sys.path.insert(0, base_path)
    import distutilazy

setupenv()
