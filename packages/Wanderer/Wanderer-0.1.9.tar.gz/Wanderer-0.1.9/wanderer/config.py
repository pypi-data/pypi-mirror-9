# -*- coding: utf-8 -*-
import os
from wanderer import package_path
from .utils import load_yaml, save_yaml


class Config(dict):
    '''Configs are concatenated from defaults and a yaml config file stored
    in a wanderer config folder. We first see if the WA_CFG environment
    variable points to a wanderer config folder, if it does we load the config
    from the wanderer.yml file within it. If not, we copy the default wanderer
    config from within this package to your user home directory, and use that.
    '''

    env_var = 'WA_CFG'
    default_config_root = os.path.expanduser('~/.wanderer')
    default_config_name = 'wanderer.yml'

    def __init__(self, *args, **defaults):
        self.defaults = defaults
        self.refresh()

    def __getattr__(self, attr):
        if attr.upper() in self: # Redirect attribute lookup to dict keys
            return self[attr.upper()]
        raise AttributeError

    def refresh(self):
        '''Refresh config from defaults and load the yaml config again.'''
        self.clear()
        self.update(self.defaults)
        self.load()

    def load(self):
        '''Load config from disk. Search for the '''

        root = os.environ.get(self.env_var)

        if not os.path.exists(root):
            shutil.copytree(package_path('.wanderer'), cfg_path)

        self.root = root
        self.path = os.path.join(self.root, self.default_config_name)

        try:
            data = load_yaml(self.path)
        except KeyError:
            raise EnvironmentError('Could not load: ' + self.path)

        self.update(data)

    def relative_path(self, *path):
        '''Returns a path relative to config root.'''

        fullpath = os.path.abspath(os.path.join(self.root, *path))
        return fullpath.replace("\\", "/")
