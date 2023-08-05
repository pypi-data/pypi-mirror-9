# -*- coding: utf-8 -*-

__title__ = 'Wanderer'
__author__ = 'Dan Bradham'
__email__ = 'danielbradham@gmail.com'
__url__ = 'http://github.com/danbradham/wanderer.git'
__version__ = '0.1.4'
__license__ = 'MIT'
__description__ = '''A roaming CG project.'''

# Python 3 compatibility
try:
    basestring
except NameError:
    basestring = str

import sys
import os

platform = sys.platform.rstrip('1234567890').lower()
if platform == 'darwin': # Use osx instead of darwin
    platform = 'osx'
os.environ['WA_OS'] = platform # Easy access to system platform

from .app import Wanderer
from . import env
