# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import, print_function

import click

from .main import hatcher
from .utils import pass_brood_client


@hatcher.group('organizations')
def organizations():
    """Perform operations on organizations.
    """


@organizations.command('create', help='Create a new organization.')
@click.argument('name')
@click.argument('description')
@pass_brood_client
def create_organization(brood_client, name, description):
    brood_client.create_organization(name, description)


@organizations.command(
    'list',
    help='List all of the organizations in a brood instance.')
@pass_brood_client
def list_organizations(brood_client):
    for organization in sorted(brood_client.list_organizations()):
        print(organization)
