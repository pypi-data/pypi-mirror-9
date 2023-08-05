# -*- coding: utf-8 -*-
import os
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
