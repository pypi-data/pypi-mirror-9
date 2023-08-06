# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
wanderer config
===============

Access the current projects configuration::

    wanderer config get components

Will echo the components section of the projects configuration.

'''

import os
from ..packages import click
from ..packages import yaml


@click.group()
@click.pass_context
def cli(ctx):
    '''Print information about the current wanderer context. Both get and set
    commands accept a key argument. Key arguments can be a dotted path pointing
    to a subkey in the configuration.'''


@cli.command()
@click.argument('key')
@click.pass_context
def get(ctx, key):
    '''Get a key from the config'''

    wanderer = ctx.obj

    value = getattr(wanderer.config, key, None)

    if value:
        click.echo(yaml.safe_dump(value, default_flow_style=False))
