# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import, print_function

import click
from tabulate import tabulate

from .main import hatcher
from .utils import pass_organization, pass_brood_client


@hatcher.group('users')
def users():
    """Perform operations on users.
    """


@hatcher.group('api-tokens')
def api_tokens():
    """Perform API token actions
    """


@users.command('create')
@click.argument('organization')
@click.argument('email')
@pass_organization
def create_user(organization, email):
    """Create a new user.
    """
    organization.create_user(email)


@users.command('delete')
@click.argument('organization')
@click.argument('email')
@pass_organization
def delete_user(organization, email):
    """Delete a user.
    """
    organization.user(email).delete()


@api_tokens.command('create')
@click.argument('name')
@pass_brood_client
def create_api_token(brood_client, name):
    """Create an API token.

    """
    response = brood_client.create_api_token(name)
    name = response['name']
    token = response['token']
    rows = [(name, token)]
    click.echo(tabulate(rows, ['New Token Name', 'New Token']))


@api_tokens.command('delete')
@click.argument('name')
@pass_brood_client
def delete_api_token(brood_client, name):
    """Delete an API token.

    """
    brood_client.delete_api_token(name)


@api_tokens.command('list')
@pass_brood_client
def list_api_tokens(brood_client):
    """List API token metadata.

    """
    tokens = brood_client.list_api_tokens()

    header = ['Name', 'Created', 'Last Used']
    token_iter = (
        (token['name'], token['created'], token['last_used'])
        for token in tokens
    )
    tokens = sorted(token_iter, key=lambda t: t[0])
    click.echo(tabulate(tokens, header))
