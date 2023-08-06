# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
wanderer bootstrap
==================

Bootstrap a new wanderer project::

    wanderer bootstrap
'''

import os
from ..packages import click
from .. import Wanderer, FilePath


@click.group(invoke_without_command=True)
@click.option('--path',
              prompt=("Insert the full path to your new project:\n\n"
                      "    C:\\path\\to\\MyProject\n\n"),
              help='Path to new project')
@click.option('--config',
              help='Path to a wanderer configuration',
              required=False)
def cli(path, config):
    '''Bootstrap a new project from the specific configuration.'''

    if not config:
        config = click.prompt(
            'Path to the config you would like to use. All '
            'environment variables or user variables will be expanded.:\n\n'
            '    C:\\path\\to\\.wanderer\n\n',
            default='default')

    config = config if config != 'default' else None

    Wanderer.bootstrap(path, config)
