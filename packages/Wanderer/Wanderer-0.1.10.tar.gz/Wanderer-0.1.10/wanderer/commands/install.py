# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
wanderer install
================

A wrapper around python pip allowing you to install packages dirctly to a
wanderer project::

    wanderer install hotline

Installs a package named hotline to the following python site in your project::

    $WA_PROJECT/.wanderer/environ/python/lib/site-packages

Let's install hotline again, but this time from it's github repository.

    wanderer install git+git@github.com/danbradham/hotline.git
'''

import os
import click
from .. import Wanderer


@click.group(invoke_without_command=True)
@click.argument('package')
@click.pass_context
def cli(ctx, package):
    '''A wrapper around python pip allowing you to install packages dirctly to
    a wanderer project::

        wanderer install hotline

    Installs a package named hotline to the following python site in your
    project::

        $WA_PROJECT/.wanderer/environ/python/lib/site-packages

    Let's install hotline again, but this time from it's github repository::

        wanderer install git+git@github.com:danbradham/hotline.git
    '''

    wanderer = ctx.obj
    wanderer.install(package)
