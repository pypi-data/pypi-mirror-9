#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import click
from .app import Wanderer
from . import commands


class WandererCli(click.MultiCommand):
    '''Lazily imports interfaces from wanderer.commands package.'''

    def list_commands(self, ctx):
        cmds = [cmd for cmd in dir(commands) if not cmd.startswith('__')]
        return sorted(cmds)

    def get_command(self, ctx, name):
        cmd_module = getattr(commands, name)
        return cmd_module.cli


@click.group(cls=WandererCli)
@click.option('--debug/--no-debug', default=False)
@click.pass_context
def cli(ctx, debug):
    '''Wanderer Command Line Tools'''

    ctx.obj = Wanderer.from_path(os.getcwd())


def main():
    cli()


if __name__ == '__main__':
    main()
