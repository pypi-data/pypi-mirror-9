"""

    distutilazy.command
    -----------

    Extra commands for setup.py using classes provided by distutilazy

    :license: MIT, see LICENSE for more details.
"""

import os
import sys

__all__ = ["clean_pyc", "clean_all", "bdist_pyinstaller", "test"]

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if not base_dir in sys.path:
    if len(sys.path):
        sys.path.insert(1, base_dir)
    else:
        sys.path.append(base_dir)


