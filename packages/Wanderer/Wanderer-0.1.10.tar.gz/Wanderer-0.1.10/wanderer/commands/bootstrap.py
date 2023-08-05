# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
wanderer bootstrap
==================

Bootstrap a new wanderer project::

    wanderer bootstrap
'''

import os
import click
from .. import Wanderer


@click.group(invoke_without_command=True)
@click.option('--path',
              prompt=("Insert the full path to your new project:\n\n"
                      "    C:\path\to\MyProject\n\n"),
              help='Path to new project')
@click.option('--config',
              help='Path to a wanderer configuration',
              required=False)
def cli(path, config):
    '''Bootstrap a new project from the specific configuration.'''

    path = os.path.expandvars(os.path.expanduser(path))

    if not config:
        config = click.prompt("Path to the config you'd like to use:\n\n"
                              "    C:\path\to\.wanderer\n\n",
                              default='default')
        if not config == 'default':
            config = os.path.expandvars(os.path.expanduser(config))
        else:
            config = None


    Wanderer.bootstrap(path, config)
