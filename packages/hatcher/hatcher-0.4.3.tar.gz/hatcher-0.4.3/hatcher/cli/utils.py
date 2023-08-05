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

from requests import HTTPError
import click

from hatcher.api import BroodClient


class BroodClientProxy(object):
    """A proxy object to the ``BroodClient`` that handles lazy verification
    of the brood ``url``.  When a subcommand is executed, this proxy
    will automatically verify that the required ``url`` is set; if not,
    will exit with an error using the standard ``click`` interfaces.

    """

    def __init__(self, url, auth, url_param, ctx, verify_ssl=True):
        self.url = url
        self.auth = auth
        self.url_param = url_param
        self.ctx = ctx
        self.brood_client = None
        self.verify_ssl = verify_ssl

    def __getattr__(self, name):
        if self.url is None:
            self.ctx.fail(self.url_param.get_missing_message(self.ctx))
        if self.brood_client is None:
            self.brood_client = BroodClient.from_url(
                self.url, auth=self.auth, verify_ssl=self.verify_ssl)
        return getattr(self.brood_client, name)


class HTTPErrorHandlingGroup(click.Group):

    def invoke(self, ctx):
        try:
            return super(HTTPErrorHandlingGroup, self).invoke(ctx)
        except HTTPError as exc:
            response = exc.response
            content_type = response.headers.get('Content-Type', '')
            if content_type == 'application/json':
                error = response.json()
                if 'error' in error:
                    click.echo(click.style(error['error'], fg='red'))
                    sys.exit(1)
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


def handle_upload_errors(fn):
    # Due to the special handling of 401, 403 and 404 at the nginx level
    # for uploads, nginx always rewrites 401 and 404 errors while
    # uploading artefacts.  That necessetates special error handling for
    # uploads.
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except HTTPError as exc:
            status_code = exc.response.status_code
            if status_code == 401:
                click.echo(click.style('Authentication failed', fg='red'))
                sys.exit(1)
            elif status_code == 404:
                repository = kwargs.get('repository', None)
                if repository is None:
                    error = 'Not found'
                else:
                    repo_name = '{}/{}'.format(
                        repository.organization_name, repository.name)
                    error = 'No such repository: {!r}'.format(repo_name)
                click.echo(click.style(error, fg='red'))
                sys.exit(1)
            raise
    return wrapper
