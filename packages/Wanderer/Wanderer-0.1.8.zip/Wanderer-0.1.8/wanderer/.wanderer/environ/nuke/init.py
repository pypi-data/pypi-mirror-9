# -*- coding: utf-8 -*-
import nuke
import sys
platform = sys.platform.rstrip('1234567890').lower()
if platform == 'darwin': # Use osx instead of darwin
    platform = 'osx'

nuke.pluginAddPath('./gizmos')
nuke.pluginAddPath('./python')
nuke.pluginAddPath('./plugins')
nuke.pluginAddPath('./plugins/' + platform)
