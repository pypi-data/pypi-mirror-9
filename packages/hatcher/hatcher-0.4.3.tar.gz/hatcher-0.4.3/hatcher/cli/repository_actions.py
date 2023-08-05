#
# Canopy product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import, print_function

import glob
import json
import os.path

import click
from tabulate import tabulate
from clint.textui import colored, progress, puts

from .main import hatcher
from .utils import handle_upload_errors, pass_organization, pass_repository


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


@apps.command('upload', help='Upload a single app to a repository.')
@click.argument('organization')
@click.argument('repository')
@click.argument('filename')
@click.option('--force', default=False, is_flag=True)
@pass_repository
@handle_upload_errors
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


@runtimes.command('upload', help='Upload a single runtime to a repository.')
@click.argument('organization')
@click.argument('repository')
@click.argument('filename')
@click.option('--force', default=False, is_flag=True)
@pass_repository
@handle_upload_errors
def upload_runtime(repository, filename, force):
    repository.upload_runtime(filename, overwrite=force)


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


@eggs.command('upload', help='Upload a single egg to a repository.')
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('filename')
@click.option('--force', default=False, is_flag=True)
@pass_repository
@handle_upload_errors
def upload_egg(repository, platform, filename, force):
    repository.platform(platform).upload_egg(filename, overwrite=force)


@eggs.command('batch-upload',
              help='Upload a batch of eggs in a directory.')
@click.argument('organization')
@click.argument('repository')
@click.argument('platform')
@click.argument('directory')
@click.option('--force', default=False, is_flag=True)
@pass_repository
@handle_upload_errors
def batch_upload_eggs(repository, platform, directory, force):
    platform_repository = repository.platform(platform)
    files = glob.glob(os.path.join(directory, "*.egg"))
    errors = []
    for filename in progress.bar(files):
        try:
            platform_repository.upload_egg(filename, overwrite=force)
        except Exception as e:
            puts(colored.red(str(e)))
            errors.append(filename)
    for error in errors:
        puts(colored.red(error))


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
