# -*- coding: utf-8 -*-
__title__ = 'Wanderer'
__author__ = 'Dan Bradham'
__email__ = 'danielbradham@gmail.com'
__url__ = 'http://github.com/danbradham/wanderer.git'
__version__ = '0.2.4'
__license__ = 'MIT'
__description__ = '''A roaming CG project.'''

import sys
import os
from ._compat import *
from .filepath import FilePath

platform = sys.platform.rstrip('1234567890').lower()
if platform == 'darwin': # Use osx instead of darwin
    platform = 'osx'
os.environ['WA_OS'] = platform # Easy access to system platform

# Package relative path joining
package_path = FilePath(__file__).dirname.join

# Import main API
from .app import Wanderer
from .models import *
from .utils import first
