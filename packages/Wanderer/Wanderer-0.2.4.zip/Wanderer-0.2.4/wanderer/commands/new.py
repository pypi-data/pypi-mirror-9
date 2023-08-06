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
from ..utils import first


@click.group()
@click.pass_context
def cli(ctx):
    '''Print information about the current wanderer context.'''


@cli.command()
@click.option('--template', help='Name of template to use')
@click.argument('cat')
@click.argument('name')
@click.pass_context
def asset(ctx, template, cat, name):
    '''Create a new asset'''

    wanderer = ctx.obj
    wanderer.new_asset(cat=cat, name=name, template=template)


@cli.command()
@click.option('--template', help='Name of template')
@click.argument('name', required=False)
@click.pass_context
def sequence(ctx, template, name):
    '''Create a new sequence'''

    wanderer = ctx.obj
    wanderer.new_sequence(name=name, template=template)


@cli.command()
@click.option('--template', help='Name of template')
@click.argument('sequence')
@click.argument('name')
@click.pass_context
def shot(ctx, template, sequence, name):
    '''Create a new shot in a sequence'''

    wanderer = ctx.obj
    seq = first(wanderer.find_sequence(name=sequence))

    if not seq:
        click.echo('Could not find a sequence named: {0}'.format(sequence))
        return

    seq.new_shot(name=name, template=template)


@cli.command()
@click.option('--template', help='Name of template')
@click.option('--cat', required=False)
@click.argument('asset')
@click.argument('name')
@click.pass_context
def asset_component(ctx, template, cat, asset, name):
    '''Create a new component in an asset'''

    cat = cat or '*'

    wanderer = ctx.obj
    asses = list(wanderer.find_asset(cat=cat, name=asset))

    if len(asses) > 1:
        click.echo('More than one asset exists with that name...\n'
                   'Specify a category using the --cat option')
        return

    if len(shots) < 1:
        click.echo('Could not find a shot named: {1}'.format(shot))
        return

    asses[0].new_component(name=name, template=template)


@cli.command()
@click.option('--template', help='Name of template')
@click.option('--sequence', help='Name of the sequence')
@click.argument('shot')
@click.argument('name')
@click.pass_context
def shot_component(ctx, template, sequence, shot, name):
    '''Create a new component in a shot'''

    sequence = sequence or '*'

    wanderer = ctx.obj
    shots = list(wanderer.find_shot(sequence=sequence, name=shot))

    if len(shots) > 1:
        click.echo('More than one shot exists with that name...\n'
                   'Specify a sequence using the --sequence option')
        return

    if len(shots) < 1:
        click.echo('Could not find a shot named: {1}'.format(shot))
        return

    shots[0].new_component(name=name, template=template)
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
from ..utils import first


@click.group()
@click.pass_context
def cli(ctx):
    '''Print information about the current wanderer context.'''


@cli.command()
@click.option('--template', help='Name of template to use')
@click.argument('cat')
@click.argument('name')
@click.pass_context
def asset(ctx, template, cat, name):
    '''Create a new asset'''

    wanderer = ctx.obj
    wanderer.new_asset(cat=cat, name=name, template=template)


@cli.command()
@click.option('--template', help='Name of template')
@click.argument('name', required=False)
@click.pass_context
def sequence(ctx, template, name):
    '''Create a new sequence'''

    wanderer = ctx.obj
    wanderer.new_sequence(name=name, template=template)


@cli.command()
@click.option('--template', help='Name of template')
@click.argument('sequence')
@click.argument('name')
@click.pass_context
def shot(ctx, template, sequence, name):
    '''Create a new shot in a sequence'''

    wanderer = ctx.obj
    seq = first(wanderer.find_sequence(name=sequence))

    if not seq:
        click.echo('Could not find a sequence named: {0}'.format(sequence))
        return

    seq.new_shot(name=name, template=template)


@cli.command()
@click.option('--template', help='Name of template')
@click.option('--cat', required=False)
@click.argument('asset')
@click.argument('name')
@click.pass_context
def asset_component(ctx, template, cat, asset, name):
    '''Create a new component in an asset'''

    cat = cat or '*'

    wanderer = ctx.obj
    asses = list(wanderer.find_asset(cat=cat, name=asset))

    if len(asses) > 1:
        click.echo('More than one asset exists with that name...\n'
                   'Specify a category using the --cat option')
        return

    if len(asses) < 1:
        click.echo('Could not find a asset named: {0}'.format(asset))
        return

    try:
        asses[0].new_component(name=name, template=template)
    except Exception as e:
        click.echo(e)

@cli.command()
@click.option('--template', help='Name of template')
@click.option('--sequence', help='Name of the sequence')
@click.argument('shot')
@click.argument('name')
@click.pass_context
def shot_component(ctx, template, sequence, shot, name):
    '''Create a new component in a shot'''

    sequence = sequence or '*'

    wanderer = ctx.obj
    shots = list(wanderer.find_shot(sequence=sequence, name=shot))

    if len(shots) > 1:
        click.echo('More than one shot exists with that name...\n'
                   'Specify a sequence using the --sequence option')
        return

    if len(shots) < 1:
        click.echo('Could not find a shot named: {0}'.format(shot))
        return

    try:
        shots[0].new_component(name=name, template=template)
    except Exception as e:
        click.echo(e)
