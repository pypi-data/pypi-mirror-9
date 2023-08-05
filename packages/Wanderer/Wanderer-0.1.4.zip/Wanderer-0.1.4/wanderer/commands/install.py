# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
wanderer install
================

A wrapper around python pip allowing you to install packages dirctly to a
wanderer project::

    wanderer install hotline

Installs a package named hotline to the following python site in your project::

    $WA_PROJECT/.wanderer/environ/Python/common

This works perfectly if you know that the package you are installing is a pure
python package. If you are installing a package with lots of dependencies or a
c extension component, use the --os-specific option. This will install your
package to one of the following locations.

 * $WA_PROJECT/.wanderer/environ/Python/linux
 * $WA_PROJECT/.wanderer/environ/Python/osx
 * $WA_PROJECT/.wanderer/environ/Python/win

Let's install hotline again, but this time from it's github repository.

    wanderer install git+git@github.com:danbradham/hotline.git
'''

import os
import click
from .. import Wanderer


@click.group(invoke_without_command=True)
@click.argument('package')
@click.option('--os_specific', is_flag=True,
              help='Install to an os-specific py site')
@click.pass_context
def cli(ctx, package, os_specific):
    '''A wrapper around python pip allowing you to install packages dirctly to
    a wanderer project::

        wanderer install hotline

    Installs a package named hotline to the following python site in your
    project::

        $WA_PROJECT/.wanderer/environ/Python/common

    This works fine if you know that the package you are installing is a
    pure python package. If you are installing a package with lots of
    dependencies or a c extension component, use the --os-specific option.
    This will install your package to one of the following locations.

     * $WA_PROJECT/.wanderer/environ/Python/linux
     * $WA_PROJECT/.wanderer/environ/Python/osx
     * $WA_PROJECT/.wanderer/environ/Python/win

    Let's install hotline again, but this time from it's github repository::

        wanderer install git+git@github.com:danbradham/hotline.git
    '''

    wanderer = ctx.obj
    wanderer.install(package, os_specific)
