#
# Canopy product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import, print_function

from functools import wraps
import sys

from requests.exceptions import HTTPError, SSLError
import click

from hatcher.errors import ChecksumMismatchError
from hatcher.api import BroodClient


class BroodClientProxy(object):
    """A proxy object to the ``BroodClient`` that handles lazy verification
    of the brood ``url``.  When a subcommand is executed, this proxy
    will automatically verify that the required ``url`` is set; if not,
    will exit with an error using the standard ``click`` interfaces.

    """

    def __init__(self, url, auth, url_param, ctx, verify_ssl=True,
                 debug=False):
        self.url = url
        self.auth = auth
        self.url_param = url_param
        self.ctx = ctx
        self.brood_client = None
        self.verify_ssl = verify_ssl
        self.debug = debug

    def __getattr__(self, name):
        if self.url is None:
            raise click.MissingParameter(ctx=self.ctx, param=self.url_param)
        if self.brood_client is None:
            self.brood_client = BroodClient.from_url(
                self.url, auth=self.auth, verify_ssl=self.verify_ssl)
        return getattr(self.brood_client, name)


class _ErrorHandlingMixin(object):

    def invoke(self, ctx):
        try:
            return super(_ErrorHandlingMixin, self).invoke(ctx)
        except ChecksumMismatchError as exc:
            if ctx.obj.debug:
                raise
            click.echo(click.style(str(exc), fg='red'), err=True)
            sys.exit(-1)
        except HTTPError as exc:
            if ctx.obj.debug:
                raise
            response = exc.response
            content_type = response.headers.get('Content-Type', '')
            if content_type == 'application/json':
                error = response.json()
                if 'error' in error:
                    click.echo(click.style(error['error'], fg='red'), err=True)
                    sys.exit(-1)
            raise
        except SSLError as exc:
            if ctx.obj.debug:
                raise
            error = 'SSL error: {}'.format(str(exc))
            url = ctx.obj.url
            click.echo(click.style(str(exc), fg='red'), err=True)
            click.echo(
                'To connect to {} insecurely, pass the `--insecure` flag to '
                'hatcher.'.format(url), err=True)
            sys.exit(-1)
        except (click.ClickException, click.Abort):
            # We don't want to intercept internal click exceptions here.
            raise
        except Exception as exc:
            if ctx.obj.debug:
                raise
            click.echo(click.style('Unexpected error', fg='red'), err=True)
            click.echo(click.style(repr(exc), fg='red'), err=True)
            sys.exit(-1)


class ErrorHandlingGroup(_ErrorHandlingMixin, click.Group):
    pass


class HTTPErrorHandlingUploadCommand(_ErrorHandlingMixin, click.Command):

    def invoke(self, ctx):
        try:
            return super(HTTPErrorHandlingUploadCommand, self).invoke(ctx)
        except HTTPError as exc:
            if ctx.obj.debug:
                raise
            status_code = exc.response.status_code
            if status_code == 401:
                click.echo(click.style('Authentication failed', fg='red'),
                           err=True)
                sys.exit(-1)
            elif status_code == 404:
                params = ctx.params
                organization_name = params.get('organization')
                repository_name = params.get('repository')
                if repository_name is None or organization_name is None:
                    error = 'Not found'
                else:
                    repo_name = '{}/{}'.format(
                        organization_name, repository_name)
                    error = 'No such repository: {!r}'.format(repo_name)
                click.echo(click.style(error, fg='red'), err=True)
                sys.exit(-1)
            raise


pass_brood_client = click.make_pass_decorator(BroodClientProxy)


def add_arguments(fn, *arguments):
    """Add click arguments to a function.  The arguments will appear in the
    CLI in the same order as they are passed to this function.

    """
    for argname in reversed(arguments):
        fn = click.argument(argname)(fn)
    return fn


def pass_organization(fn):
    @wraps(fn)
    def wrapper(brood_client, organization, *args, **kwargs):
        org = brood_client.organization(organization)
        return fn(organization=org, *args, **kwargs)
    return pass_brood_client(wrapper)


def pass_repository(fn):
    @wraps(fn)
    def wrapper(brood_client, organization, repository, *args, **kwargs):
        repo = brood_client.organization(organization).repository(repository)
        return fn(repository=repo, *args, **kwargs)
    return pass_brood_client(wrapper)


def pass_team(fn):
    @wraps(fn)
    def wrapper(brood_client, organization, team, *args, **kwargs):
        org = brood_client.organization(organization)
        team = org.team(team)
        return fn(team=team, *args, **kwargs)
    return pass_brood_client(wrapper)
