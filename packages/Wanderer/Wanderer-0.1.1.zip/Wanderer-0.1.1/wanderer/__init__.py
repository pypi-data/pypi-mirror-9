# -*- coding: utf-8 -*-

__title__ = 'Wanderer'
__author__ = 'Dan Bradham'
__email__ = 'danielbradham@gmail.com'
__url__ = 'http://github.com/danbradham/wanderer.git'
__version__ = '0.1.1'
__license__ = 'MIT'
__description__ = '''A roaming CG project.'''

# Python 3 compatibility
try:
    basestring
except NameError:
    basestring = str

from .app import Wanderer
