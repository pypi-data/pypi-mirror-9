# -*- coding: utf-8 -*-
import os
import sys
from .filepath import FilePath
from .packages import yaml

def load_yaml(yml_filepath):
    '''Load yaml file

    :param yml_filepath: path to yaml file

    :return: dict
    '''

    with open(yml_filepath) as yml_file:
        data = yaml.load(yml_file)

    return data


def save_yaml(yml_filepath, data):
    '''Save yaml file

    :param yml_filepath: path to yaml file
    :param data: python dict to save
    '''
    with open(yml_filepath, 'w') as yml_file:
        yml_file.write(yaml.safe_dump(dict(data), default_flow_style=False))

    return True


def find_project(path):
    '''Given a file path, return a Wanderer project root.

    :param path: Path to walk up from'''

    path = FilePath(path)

    project = None
    for root, subdirs, files in path.walk_up():
        if '.wanderer' in subdirs:
            return root

    return


def first(gen):
    '''Return the first element in a generator or None.'''

    try:
        item = gen.next()
    except StopIteration:
        return
    return item
