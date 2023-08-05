# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
wanderer uninstall
==================

A wrapper around python pip allowing you to uninstall packages from a
wanderer project::

    wanderer uninstall hotline
'''

import os
import click
from .. import Wanderer


@click.group(invoke_without_command=True)
@click.argument('package')
@click.pass_context
def cli(ctx, package):
    '''A wrapper around python pip allowing you to uninstall packages from a
    wanderer project::

        wanderer uninstall hotline
    '''

    wanderer = ctx.obj
    wanderer.uninstall(package)
