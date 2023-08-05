# -*- coding: utf-8 -*-

__title__ = 'Wanderer'
__author__ = 'Dan Bradham'
__email__ = 'danielbradham@gmail.com'
__url__ = 'http://github.com/danbradham/wanderer.git'
__version__ = '0.1.7'
__license__ = 'MIT'
__description__ = '''A roaming CG project.'''

# Python 3 compatibility
try:
    basestring
except NameError:
    basestring = str

import sys
import os
from functools import partial

platform = sys.platform.rstrip('1234567890').lower()
if platform == 'darwin': # Use osx instead of darwin
    platform = 'osx'
os.environ['WA_OS'] = platform # Easy access to system platform

# Package relative path joining
package_path = partial(os.path.join, os.path.dirname(__file__))

# Global variable to test if wheel is installed
try:
    import wheel
    WHEEL_INSTALLED = True
except ImportError:
    WHEEL_INSTALLED = False

# Import main API
from .app import Wanderer
