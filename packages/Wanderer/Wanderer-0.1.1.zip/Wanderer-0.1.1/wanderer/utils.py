# -*- coding: utf-8 -*-
import os
import collections


def walk_up(root, steps=20):
    '''Walk up a directory tree. Similar to os.walk but excludes stepping into
    subdirs.

    :param root: Directory to walk up from
    :param steps: Maximum steps taken up a tree
    :returns: (root, subdirs, files) such that a path can be constructed
    joining root with a subdir or file.'''

    for i in xrange(steps):
        files = set(os.listdir(root))
        dirs = set([f for f in files if os.path.isdir(os.path.join(root, f))])
        files -= dirs
        yield root, sorted(list(dirs)), sorted(list(files))

        root = os.path.dirname(root)


def env_from_dict(d):
    '''Sets environment variables defined in a dictionary. The dictionary
    should use lists to store multiple paths per environment variable. Any
    environment variables used in paths will be expanded.

    :param d: Environment dict'''

    for key, value in d.iteritems():
        path = None
        if isinstance(value, basestring):
            path = os.path.abspath(os.path.expandvars(value))
        elif isinstance(value, collections.Sequence):
            path = os.pathsep.join([os.path.abspath(os.path.expandvars(v))
                                    for v in value])
        if path:
            if os.environ.get(key, None):
                os.environ[key] = path + os.pathsep + os.environ[key]
            else:
                os.environ[key] = path


def load_yaml(yml_filepath):
    '''Load yaml file

    :param yml_filepath: path to yaml file

    :return: dict
    '''

    import yaml

    with open(yml_filepath) as yml_file:
        data = yaml.load(yml_file)

    return data


def save_yaml(yml_filepath, data):
    '''Save yaml file

    :param yml_filepath: path to yaml file
    :param data: python dict to save
    '''

    import yaml

    with open(yml_filepath, 'w') as yml_file:
        yml_file.write(yaml.safe_dump(dict(data), default_flow_style=False))

    return True
