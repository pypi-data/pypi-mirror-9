#
# Canopy product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import, print_function

import json
import os.path

import click
from tabulate import tabulate
from clint.textui import progress
from requests import HTTPError

from ..core.utils import EggMetadata, RuntimeMetadata
from ..errors import ChecksumMismatchError
from .main import hatcher
from .utils import (
    pass_organization, pass_repository, HTTPErrorHandlingUploadCommand)


@hatcher.group('repositories')
def repositories():
    """Perform operations on repositories.
    """


@hatcher.group('apps')
def apps():
    """Perform operations on apps.
    """


@hatcher.group('eggs')
def eggs():
    """Perform operations on eggs.
    """


@hatcher.group('runtimes')
def runtimes():
    """Perform operations on runtimes.
    """


@repositories.command(
    'list',
    help='List all of the repositories from a given organization.')
@click.argument('organization')
@pass_organization
def list_repositories(organization):
    for repository in sorted(organization.list_repositories()):
        print(repository)


@repositories.command('create', help='Create a new repository.')
@click.argument('organization')
@click.argument('repository')
@click.argument('description')
@pass_organization
def create_repository(organization, repository, description):
    organization.create_repository(repository, description)


@repositories.command('delete', help='Delete a repository.')
@click.argument('organization')
@click.argument('repository')
@click.option('--force', default=False, is_flag=True)
@pass_repository
def delete_repository(repository, force):
    repository.delete(force=force)


@apps.command('list')
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@pass_repository
def list_apps(repository, platform):
    """List all apps in a repository.
    """
    sort_key = lambda app: tuple(a.lower() for a in app)
    apps = repository.platform(platform).list_apps()
    sorted_apps = sorted(apps, key=sort_key)
    headers = ['App Name', 'Version', 'Python Tag']
    click.echo(tabulate(sorted_apps, headers=headers, floatfmt='f'))


@apps.command('upload', help='Upload a single app to a repository.',
              cls=HTTPErrorHandlingUploadCommand)
@click.argument('organization')
@click.argument('repository')
@click.argument('filename')
@click.option('--force', default=False, is_flag=True)
@pass_repository
def upload_app(repository, filename, force):
    repository.upload_app(filename, overwrite=force)


@apps.command('metadata', help='Get the metadata for a single app.')
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('app_id')
@click.argument('version')
@pass_repository
def app_metadata(repository, platform, python_tag, app_id, version):
    metadata = repository.platform(platform).app_metadata(
        python_tag, app_id, version)
    print(json.dumps(metadata, sort_keys=True, indent=2))


@runtimes.command('list')
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@pass_repository
def list_runtimes(repository, platform):
    """List all runtimes in a repository.
    """
    for runtime in sorted(repository.platform(platform).list_runtimes(),
                          key=lambda s: s.lower()):
        print(runtime)


def _upload_verify(filename, get_remote_metadata, metadata_cls,
                   do_upload, verify, force, platform=None):
    """Handle uploading a file with the feature to verify if the same file
    has been uploaded before.

    Parameters
    ----------
    filename : str
        The path to the file to upload
    get_remote_metadata : callable
        A closure that accepts a local metadata specification and will
        return the remote metadata dictionary.
    metadata_cls : type
        A local metadata specification type. One of
        :class:`~.EggMetadata` or :class:`~.RuntimeMetadata`.
    do_upload : callable
        A closure that takes no arguments and will upload the file.
    verify : bool
        True to verify if the file has been uploaded before; False to
        simply attempt to upload.
    force : bool
        True to skip any verification and force-overwrite the egg if
        it already exists on the server.

    """
    # Force overrides verify
    if verify and not force:
        local_metadata = metadata_cls.from_file(filename, platform)
        try:
            remote_metadata = get_remote_metadata(local_metadata)
        except HTTPError as exc:
            if exc.response.status_code != 404:
                raise
            # If the egg is not found (status code 404), do the upload.
            return do_upload()
        else:
            sha256 = local_metadata.sha256
            if sha256 != remote_metadata['sha256']:
                raise ChecksumMismatchError(
                    'A file called {} has already been uploaded with '
                    'different content'.format(os.path.basename(filename)))
            # The sha256 matches, we don't need to upload.
            return
    else:
        return do_upload()


@runtimes.command('upload', help='Upload a single runtime to a repository.',
                  cls=HTTPErrorHandlingUploadCommand)
@click.argument('organization')
@click.argument('repository')
@click.argument('filename')
@click.option('--force', default=False, is_flag=True)
@click.option('--verify/--no-verify', default=False)
@pass_repository
def upload_runtime(repository, filename, force, verify):
    def _do_upload():
        repository.upload_runtime(filename, overwrite=force)

    def _get_remote_metadata(local_metadata):
        repo = repository.platform(local_metadata.platform)
        return repo.runtime_metadata(
            local_metadata.python_tag, local_metadata.full_version)

    _upload_verify(
        filename, _get_remote_metadata, RuntimeMetadata, _do_upload,
        verify=verify, force=force)


@runtimes.command('download')
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('version')
@click.argument('destination', required=False)
@pass_repository
def download_runtime(repository, platform, python_tag, version,
                     destination=None):
    """Download a runtime archive.
    """
    from .progress_bar import progressbar

    if destination is None:
        destination = os.getcwd()

    length, iterator = repository.platform(platform).iter_download_runtime(
        python_tag, version, destination)

    with progressbar(iterable=iterator, length=length) as bar:
        for chunk_size in bar:
            pass


@runtimes.command('metadata', help='Get the metadata for a single runtime.')
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('version')
@pass_repository
def runtime_metadata(repository, platform, python_tag, version):
    metadata = repository.platform(platform).runtime_metadata(
        python_tag, version)
    print(json.dumps(metadata, sort_keys=True, indent=2))


@eggs.command('metadata')
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('name')
@click.argument('version')
@pass_repository
def egg_metadata(repository, platform, python_tag, name, version):
    """Get the metadata for a single egg.
    """
    metadata = repository.platform(platform).egg_metadata(
        python_tag, name, version)
    click.echo(json.dumps(metadata, sort_keys=True, indent=2))


@eggs.command('download')
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('name')
@click.argument('version')
@click.argument('destination', required=False)
@pass_repository
def download_egg(repository, platform, python_tag, name, version,
                 destination=None):
    """Download an egg.
    """
    from .progress_bar import progressbar

    if destination is None:
        destination = os.getcwd()

    length, iterator = repository.platform(platform).iter_download_egg(
        python_tag, name, version, destination)

    with progressbar(iterable=iterator, length=length) as bar:
        for chunk_size in bar:
            pass


@eggs.command('delete')
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@click.argument('name')
@click.argument('version')
@pass_repository
def delete_egg(repository, platform, python_tag, name, version):
    """Delete an egg.
    """
    repository.platform(platform).delete_egg(python_tag, name, version)


@eggs.command('upload', help='Upload a single egg to a repository.',
              cls=HTTPErrorHandlingUploadCommand)
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('filename')
@click.option('--force', default=False, is_flag=True)
@click.option('--verify/--no-verify', default=False)
@pass_repository
def upload_egg(repository, platform, filename, force, verify):
    repo = repository.platform(platform)

    def _do_upload():
        repo.upload_egg(filename, overwrite=force)

    def _get_remote_metadata(local_metadata):
        return repo.egg_metadata(
            local_metadata.python_tag, local_metadata.name,
            local_metadata.full_version)

    _upload_verify(
        filename, _get_remote_metadata, EggMetadata, _do_upload, verify=verify,
        force=force, platform=platform)


@eggs.command('batch-upload',
              cls=HTTPErrorHandlingUploadCommand)
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('eggs', nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.option('--force', default=False, is_flag=True)
@pass_repository
def batch_upload_eggs(repository, platform, eggs, force):
    """Upload a batch of eggs.

    The upload will terminate on the first failure, and the indexing will be
    'transactionaly' in the sense that it will happen exactly once, once all
    the files have been successfully uploaded.
    """
    platform_repository = repository.platform(platform)

    def _do_upload(filename):
        platform_repository.upload_egg(
            filename, overwrite=force, enabled=False)

    def _get_remote_metadata(local_metadata):
        return platform_repository.egg_metadata(
            local_metadata.python_tag, local_metadata.name,
            local_metadata.full_version)

    for filename in progress.bar(eggs):
        try:
            do_upload = lambda: _do_upload(filename)
            _upload_verify(
                filename, _get_remote_metadata, EggMetadata, do_upload,
                verify=True, force=force, platform=platform)
        except Exception:
            click.echo('', err=True)  # Move to the line after the progress bar
            click.echo(
                click.style('Error uploading {}'.format(filename), fg='red'),
                err=True)
            raise
    repository.reindex(eggs)


@eggs.command('list', help='List all eggs in a repository')
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('python_tag')
@pass_repository
def list_eggs(repository, platform, python_tag):
    eggs_iter = sorted(repository.platform(platform).list_eggs(python_tag),
                       key=lambda egg: egg['name'].lower())
    eggs = [(egg['name'], egg['python_tag']) for egg in eggs_iter]
    headers = ['Egg Name', 'Python Tag']
    click.echo(tabulate(eggs, headers=headers))
