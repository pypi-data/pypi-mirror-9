# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import, print_function

import click
from tabulate import tabulate

from .main import hatcher
from .utils import pass_brood_client


@hatcher.group('platforms')
def platforms():
    """Perform operations on platforms.
    """


@hatcher.group('python-tags')
def python_tags():
    """Perform operations on PEP425 Python tags.
    """


@platforms.command('list')
@pass_brood_client
def list(brood_client):
    platforms = [[platform] for platform in brood_client.list_platforms()]
    click.echo(tabulate(platforms, headers=['Platforms']))


@python_tags.command('list')
@click.option('--all', default=False, is_flag=True,
              help='List all possible Python tags')
@pass_brood_client
def list_python_tags(brood_client, all=False):
    """List available Python tags.

    The default is to list the tags corresponding to actual Python
    implementations and versions.  When the --all option is provided,
    list all possible python tags.

    """
    tags = [[tag]
            for tag in sorted(brood_client.list_python_tags(list_all=all))]
    click.echo(tabulate(tags, headers=['Python Tag']))
