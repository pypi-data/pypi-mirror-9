# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
wanderer new
============

Create assets, sequences, shots, and components::

    wanderer new asset characters asset_a
'''

import os
from ..packages import click
from ..packages import yaml
from .. import FilePath


@click.group()
@click.pass_context
def cli(ctx):
    '''Create new assets and sequences'''


@cli.command()
@click.option('--list_categories', is_flag=True, help='List categories')
@click.option('--list_templates', is_flag=True, help='List templates')
@click.option('--template', help='Name of template to use')
@click.argument('cat', required=False)
@click.argument('name', required=False)
@click.pass_context
def asset(ctx, list_categories, list_templates, template, cat, name):
    '''Create a new asset'''

    wanderer = ctx.obj

    if list_categories:
        asset_root = FilePath('$WA_ASSETS').expand()
        click.echo('Current asset categories:')
        for c in sorted(asset_root.listdir):
            click.echo(' - {0}'.format(c))

        return

    elif list_templates:
        click.echo('Available templates:')
        for c in sorted(wanderer.config.root.join('templates').listdir):
            click.echo(' - {0}'.format(c))

        return

    if not name or not cat:
        click.echo('You must provide both a category and name. e.g.\n\n'
                   '\t wanderer new asset character My_Character')
        return

    ass = wanderer.new_asset(cat=cat, name=name, template=template)
