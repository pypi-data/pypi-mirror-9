"""
    distutilazy.command.clean_all
    -----------------------------

    Command to clean all temporary files

    :license: MIT, see LICENSE for more details.
"""

import os
import sys

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
if not base_dir in sys.path:
    if len(sys.path):
        sys.path.insert(1, base_dir)
    else:
        sys.path.append(base_dir)

import distutilazy.pyinstaller

class clean_all(distutilazy.pyinstaller.clean_all):
    pass
