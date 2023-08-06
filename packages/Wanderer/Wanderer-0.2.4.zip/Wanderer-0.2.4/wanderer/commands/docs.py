# -*- coding: utf-8 -*-
#!/usr/bin/env python
'''
wanderer docs
=============

View the documentation for Wanderer::

    wanderer docs
'''

from ..packages import click
import webbrowser


@click.group(invoke_without_command=True)
def cli():
    '''Command for viewing documentation.'''

    webbrowser.open('http://wanderer.readthedocs.org')

