# -*- coding: utf-8 -*-
'''
wanderer.app
============
Contains the main application object :class:`Wanderer`.
'''

import shutil
import os
from os.path import expanduser
import logging
import sys
import subprocess
from functools import partial
from . import utils
from .config import Config

platform = sys.platform.rstrip('1234567890').lower()
if platform == 'darwin': # Use osx instead of darwin
    platform = 'osx'
os.environ['WA_OS'] = platform # Easy access to system platform
package_path = partial(os.path.join, os.path.dirname(__file__))


class Wanderer(object):
    '''Handles all things Wanderer.'''

    defaults = {
        'debug': False,
    }

    def __init__(self):
        self.config = Config(**self.defaults)

        self.project = os.environ.setdefault('WA_PROJECT', '')
        cfg_path = os.environ.setdefault('WA_CFG', expanduser('~/.wanderer'))

        if not os.path.exists(cfg_path):
            shutil.copytree(package_path('.wanderer'), cfg_path)

        self.config.from_env('WA_CFG')

        self.setup_env(self.config['ENV'])

    def setup_env(self, d):
        '''Used for setting environments configured in your wanderer config.
        ::

            wanderer.setup_env(wanderer.config['ENV'])

        :param d: Dictionary that defines an environment.'''

        utils.env_from_dict(d)

    def launch(self, app):
        '''Used to launch a CG application in a Wanderer project environment.
        ::

            from wanderer import Wanderer
            app = Wanderer.from_path('project/path')
            app.launch('maya')

        :param app: Name of application to launch. This is used to pull in an
        app_path and env defined in your configuration.
        '''

        app_cfg = self.config['APPLICATIONS'][app.lower()]
        self.setup_env(app_cfg['ENV'])
        p = subprocess.Popen(
            os.path.abspath(app_cfg['PATH'][platform]),
            shell=True,
            env=os.environ.copy(),
            cwd=os.path.abspath(self.project))
        return p.pid

    def get_template_dir(self, template):
        '''Get the path to a template folder tree stored in your projects
        .wanderer/templates folder.

        :param template: Name of the template
        :returns: Absolute path to the template folder'''

        return self.config.relative_path('templates/', template)

    def get_template(self, template):
        '''Get a template path from your projects config formatted using the
        current context.
        :returns: Formatted path to a configured path.'''

        tmpl = self.config['TEMPLATES'][template]
        filepath = tmpl.format(**self.context.__dict__)
        return os.path.abspath(os.path.join(self.project, filepath))

    @classmethod
    def from_path(cls, path):
        '''Search the specified path for a wanderer project setting the
        necessary environment variables in the process.

        :param path: Search path
        :returns: :class:`Wanderer` instance
        '''

        project = None
        for root, subdirs, files in utils.walk_up(path):
            if '.wanderer' in subdirs:
                project = root
                break

        if project:
            os.environ['WA_PROJECT'] = project
            os.environ['WA_CFG'] = os.path.join(project, '.wanderer')

        return cls()
