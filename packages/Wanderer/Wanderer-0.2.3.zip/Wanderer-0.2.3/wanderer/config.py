# -*- coding: utf-8 -*-
import os
from wanderer import package_path
from .filepath import FilePath
from .utils import load_yaml, save_yaml


class Config(dict):
    '''Configs are concatenated from defaults and a yaml config file stored
    in a wanderer config folder. We first see if the WA_CFG environment
    variable points to a wanderer config folder, if it does we load the config
    from the wanderer.yml file within it. If not, we copy the default wanderer
    config from within this package to your user home directory, and use that.
    '''

    env_var = 'WA_CFG'
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

        root = FilePath(os.environ.get(self.env_var))

        if not root.exists:
            package_path('.wanderer').copy(root)

        self.root = root
        self.path = self.root.join(self.default_config_name)

        try:
            data = load_yaml(self.path)
        except KeyError:
            raise EnvironmentError('Could not load: ' + self.path)

        self.update(data)

    def relative_path(self, *args):
        '''Returns a path relative to config root.'''

        return self.root.join(*args).abspath
