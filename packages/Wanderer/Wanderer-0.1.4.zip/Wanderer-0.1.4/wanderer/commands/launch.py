# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
wanderer launch
===============

Launch an application in a Wanderer context::

    wanderer launch maya
'''

from subprocess import Popen
import os
import click


@click.group(invoke_without_command=True)
@click.option('--list_apps', is_flag=True, required=False)
@click.argument('application_name', nargs=-1, required=False)
@click.pass_context
def cli(ctx, list_apps, application_name):
    '''Launch an application.'''
    wanderer = ctx.obj

    if list_apps:
        click.echo(', '.join(wanderer.config['APPLICATIONS'].keys()))
        return

    if application_name:
        if not isinstance(application_name, basestring):
            application_name = ' '.join(application_name)
        click.echo('Launching ' + application_name)
        wanderer.launch(application_name)
        return

    click.echo(ctx.get_help())
