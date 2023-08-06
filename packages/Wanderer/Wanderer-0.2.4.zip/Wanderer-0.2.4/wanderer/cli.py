#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from .packages import click
from .app import Wanderer
import logging
from . import commands

WANDERER = Wanderer.from_path(os.getcwd())

class WandererCli(click.MultiCommand):
    '''Lazily imports interfaces from wanderer.commands package.'''

    def list_commands(self, ctx):
        cmds = [cmd for cmd in dir(commands) if not cmd.startswith('__')]
        return sorted(cmds)

    def get_command(self, ctx, name):
        cmd_module = getattr(commands, name)
        return cmd_module.cli


@click.group(cls=WandererCli)
@click.option('--debug/--no-debug', default=True)
@click.pass_context
def cli(ctx, debug):
    '''Wanderer Command Line Tools'''

    if debug:
        WANDERER.logger.setLevel(logging.DEBUG)
    else:
        WANDERER.logger.setLevel(logging.INFO)

    ctx.obj = WANDERER


def main():
    click.clear()
    click.echo(WANDERER.info)
    cli()


if __name__ == '__main__':
    main()
