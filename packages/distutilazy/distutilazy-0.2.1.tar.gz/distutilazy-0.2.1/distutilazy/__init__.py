"""
    distutilazy
    -----------

    Extra distutils command classes.

    :license: MIT, see LICENSE for more details.
"""

import os
import sys

__version__ = '0.2.1'
__all__ = ['clean', 'pyinstaller', 'command']

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if not base_dir in sys.path:
    if len(sys.path):
        sys.path.insert(1, base_dir)
    else:
        sys.path.append(base_dir)
