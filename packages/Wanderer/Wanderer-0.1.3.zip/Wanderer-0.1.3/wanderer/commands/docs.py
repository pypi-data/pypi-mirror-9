# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
wanderer docs
=============

View the documentation for Wanderer::

    wanderer docs view
'''

import click
import webbrowser


@click.group()
def cli():
    '''Command for viewing documentation.'''


@cli.command()
def view():
    '''View the documentation for Wanderer'''

    webbrowser.open('http://wanderer.readthedocs.org')
