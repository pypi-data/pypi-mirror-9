#
# Canopy product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import, print_function

import click

from hatcher import __version__
from hatcher.core.auth import BroodBearerTokenAuth
from hatcher.utils import command_tree_option
from .utils import BroodClientProxy, ErrorHandlingGroup


@click.group(cls=ErrorHandlingGroup)
@click.option('-u', '--url', help='The URL of the Brood server.  [required]')
@click.option('-U', '--username', help='Username for authentication.')
@click.option(
    '-p', '--password',
    help=('Password for authentication. If --username is given but '
          'password is omitted, hatcher will prompt for a password.')
)
@click.option('-t', '--token', help='Brood API token for authentication.')
@click.option('-k', '--insecure', is_flag=True, default=False,
              help='Disable SSL certificate verification')
@click.option('-d', '--debug', is_flag=True, default=False,
              help='Show traceback on error')
@command_tree_option(help='Print the full hatcher command tree.')
@click.version_option(__version__, prog_name='hatcher')
@click.pass_context
def hatcher(ctx, url, username=None, password=None, token=None,
            insecure=False, debug=False):
    """A command-line interface to Brood.
    """
    verify_ssl = not insecure

    if username is None and password is not None:
        ctx.fail('Password provided with no username')
    if username is not None and password is None:
        password = click.prompt('Password', hide_input=True)

    if username is not None:
        auth = (username, password)
    elif token is not None:
        auth = BroodBearerTokenAuth(token)
    else:
        auth = None

    url_param = next(param for param in hatcher.params
                     if param.name == 'url')
    ctx.obj = BroodClientProxy(
        url, auth, url_param, ctx, verify_ssl=verify_ssl, debug=debug)


def main():
    return hatcher(auto_envvar_prefix='HATCHER')
