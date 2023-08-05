# -*- coding: utf-8 -*-
import os
import sys


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
