# -*- coding: utf-8 -*-
import os
import collections
import sys


def walk_up(root, steps=20):
    '''Walk up a directory tree. Similar to os.walk but excludes stepping into
    subdirs.

    :param root: Directory to walk up from
    :param steps: Maximum steps taken up a tree
    :returns: (root, subdirs, files) such that a path can be constructed
    joining root with a subdir or file.
    '''

    for i in xrange(steps):
        files = set(os.listdir(root))
        dirs = set([f for f in files if os.path.isdir(os.path.join(root, f))])
        files -= dirs
        yield root, sorted(list(dirs)), sorted(list(files))

        root = os.path.dirname(root)


def walk_dn(root, steps=10):
    '''Walk through a directory tree. Similar to os.walk but takes a steps
    parameter to determine walk depth.

    :param root: Directory to walk through
    :param steps: Maximum steps taken through the tree
    :returns: (root, subdirs, files) such that a path can be constructed
    joining root with a subdir or file.
    '''

    root = os.path.normpath(root)
    depth = root.count(os.path.sep)
    max_step = depth + steps
    for root, dirs, files in os.walk(root):
        yield root, dirs, files

        depth = root.count(os.path.sep)
        if depth >= max_step:
            break


def env_set_state(env, pypath):
    '''Restore environment and pythonpath to a previous state.

    :param env: Environment retrieved using os.environ.data.copy()
    :param pypath: PYTHONPATH retrieved from sys.path
    '''

    os.environ.data = env
    sys.path[:] = pypath


def env_get_state():
    '''Retrieve the current environment and pythonpath

    :returns: Tuple containing copy of os.environ.data and sys.path
    '''

    return os.environ.data.copy(), sys.path[:]


def env_from_dict(d):
    '''Sets environment variables defined in a dictionary. The dictionary
    should use lists to store multiple paths per environment variable. Any
    environment variables used in paths will be expanded. The PYTHONPATH
    variable will be independently parsed to insert any egg archives into
    sys.path.

    :param d: Environment dict
    '''

    for key, value in d.iteritems():
        path = None
        if isinstance(value, basestring):
            path = os.path.expandvars(value)
        elif isinstance(value, collections.Sequence):
            path = os.pathsep.join([os.path.expandvars(v)
                                    for v in value])
        else:
            print 'ENV ERROR: {} invalid: {}'.format(key, value)

        if path:
            if os.environ.get(key, None):
                os.environ[key] = path + os.pathsep + os.environ[key]
            else:
                os.environ[key] = path

    pypath = d.get('PYTHONPATH', None)
    if pypath:
        paths = []
        if isinstance(pypath, basestring):
            paths.append(os.path.expandvars(pypath))
        elif isinstance(pypath, collections.Sequence):
            paths.extend([os.path.expandvars(path)
                                for path in pypath])
        else:
            print 'ENV Error: PYTHONPATH invalid: {}'.format(pypath)

        for path in paths:
            if not os.path.exists(path):
                continue

            for f in os.listdir(path):
                if f.endswith('.egg'):
                    egg_path = os.path.join(path, f)
                    if not egg_path in sys.path:
                        sys.path.insert(1, os.path.join(path, f))
            if not path in sys.path:
                sys.path.insert(1, path)


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
