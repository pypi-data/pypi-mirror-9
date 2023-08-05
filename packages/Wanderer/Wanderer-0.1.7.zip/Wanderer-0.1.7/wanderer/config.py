# -*- coding: utf-8 -*-
import os
from .utils import load_yaml, save_yaml

SUPPORTED_TYPES = ['yaml', 'yml']


class Config(dict):
    '''Yaml based config object. Instantiated like a standard dict object.
    Use from_end or from_file to load a configuration from either a config root
    folder or config file. Each top-level config key is accessible via standard
    attribute lookup. Thereforce a config key "DEBUG" is accessible through
    Config().debug and Config()["DEBUG"].'''

    def __init__(self, *args, **defaults):
        super(Config, self).__init__(*args, **defaults)
        self.root = None
        self.path = None

    def __getattr__(self, attr):
        if attr.upper() in self: # Redirect attribute lookup to dict keys
            return self[attr.upper()]
        raise AttributeError

    def from_env(self, env_var):
        '''Looks for a config file ain the specified environment variable.
        **env_var** should be either the path to a config file, or the path
        to a wanderer config folder containing a config named wanderer.yml.
        '''

        env_path = os.environ.get(env_var)

        if os.path.exists(env_path):
            if os.path.isfile(env_path):
                self.root = os.path.dirname(env_path)
                path = env_path
                self.from_file(path)
            else:
                self.root = env_path
                for typ in SUPPORTED_TYPES:
                    path = self.relative_path('wanderer.{}'.format(typ))
                    if os.path.exists(path):
                        self.from_file(path)
        else:
            raise EnvironmentError(
                '{} points to invalid path: {}'.format(env_var, env_path))

    def from_file(self, path):
        '''Update Config with values from the specified yaml config.

        :param path: path to a yaml config file'''
        ext = path.split(".")[-1]

        try:
            data = load_yaml(path)
        except KeyError:
            raise OSError("Config files must be a yaml file")

        self.update(data)

        self.path = path

    def relative_path(self, *path):
        '''Returns a path relative to config file or config root'''

        fullpath = os.path.abspath(os.path.join(self.root, *path))
        return fullpath.replace("\\", "/")

    def save(self, ext=None):
        '''Write config data to file.

        :param ext: Extension of file type'''

        if not ext:
            ext = self.path.split(".")[-1]
            path = self.path
        else:
            path = "{}.{}".format(os.path.splitext(self.path)[0], ext)

        save_yaml(path, data)
