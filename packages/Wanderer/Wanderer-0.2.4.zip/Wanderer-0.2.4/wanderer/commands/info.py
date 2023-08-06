# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
wanderer info
=============

Get some information on the current context::

    wanderer info
'''

import os
from ..packages import click
from ..packages import yaml


@click.group()
@click.pass_context
def cli(ctx):
    '''Print information about the current wanderer context.'''


@cli.command()
@click.option('--app', required=False,help='print an app environment')
@click.pass_context
def env(ctx, app):
    '''Print environment'''

    wanderer = ctx.obj

    if app:
        wanderer.setup_env(wanderer.config.applications[app.lower()]['ENV'])

    env = os.environ.copy()
    env.pop('WA_CLEAN_ENV', None)

    click.echo(yaml.dump(env, default_flow_style=False))


@cli.command()
@click.pass_context
def config(ctx):
    '''Print out the configuration'''

    wanderer = ctx.obj

    click.echo(yaml.safe_dump(dict(wanderer.config), default_flow_style=False))
