# Canopy product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import

import os

import yaml

from okonomiyaki.file_formats.egg import LegacySpecDepend

from hatcher.errors import MissingPlatformError
from .url_templates import URLS
from .utils import RuntimeMetadata, compute_sha256


class SinglePlatformRepository(object):
    """A representation of a Brood repository for a single platform.

    """

    def __init__(self, repository, platform, url_handler):
        """Create a SinglePlatformRepository.

        """
        self._repository = repository
        self.name = platform
        self._url_handler = url_handler

    def __repr__(self):
        return (
            '<{cls} organization={organization!r}, '
            'repository={repository!r}, platform={platform!r}>'.format(
                cls=type(self).__name__,
                organization=self.organization_name,
                repository=self.repository_name,
                platform=self.name,
            )
        )

    @property
    def organization_name(self):
        return self._repository.organization_name

    @property
    def repository_name(self):
        return self._repository.name

    #### Eggs #################################################################

    def list_eggs(self, python_tag):
        """Return a list of all egg filenames in a repository.

        Parameters
        ----------
        python_tag : str
            The most specific Python tag of the runtime for which egg
            compatibility is desired.  This must reference a particular
            implementation and specific ``major.minor`` Python version
            (e.g. ``pp27`` or ``cp34``), not generic Python
            compatibility or any-version (e.g. ``py27`` or ``cp3``).

        Returns
        -------
        eggs : list
            List of dictionaries in the form
            ``{'name': egg_name, 'python_tag': python_tag}``

        """
        data = self.egg_index(python_tag)
        return [{'name': egg, 'python_tag': entry['python_tag']}
                for egg, entry in data.items()]

    def egg_index(self, python_tag):
        """Return a list of all egg filenames in a repository.

        Parameters
        ----------
        python_tag : str
            The most specific Python tag of the runtime for which egg
            compatibility is desired.  This must reference a particular
            implementation and specific ``major.minor`` Python version
            (e.g. ``pp27`` or ``cp34``), not generic Python
            compatibility or any-version (e.g. ``py27`` or ``cp3``).

        """
        path = URLS.indices.eggs.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
            python_tag=python_tag,
        )
        data = self._url_handler.get_json(path)
        return data

    def egg_metadata(self, python_tag, name, version):
        """Download the metadata for an egg.

        """
        path = self._egg_url(
            URLS.metadata.artefacts.eggs, python_tag, name, version)
        return self._url_handler.get_json(path)

    def download_egg(self, python_tag, name, version, destination):
        """Download the egg specified by ``name``, ``version``, saving the
        resulting file in the ``destination`` directory.

        Parameters
        ----------
        python_tag : str
            The Python runtime compatibility of the egg, as defined in
            the ``Python Tag`` section of PEP425.
        name : str
            The name of the egg.
        version : str
            The full version specification of the egg.

        """
        metadata = self.egg_metadata(python_tag, name, version)
        expected_sha256 = metadata['sha256']

        eggname = self._egg_name(name, version)
        path = self._egg_url(
            URLS.data.eggs.download, python_tag, name, version)
        self._url_handler.download_file(
            path, destination, expected_sha256, filename=eggname)

    def iter_download_egg(self, python_tag, name, version, destination):
        """Download the egg specified by ``name``, ``version``, saving the
        resulting file in the ``destination`` directory.

        This method returns a tuple of (content_length, iterator).  The
        ``content_length`` is the total size of the download.  The
        ``iterator`` yield the size of each chunk as it is downloaded.

        Parameters
        ----------
        python_tag : str
            The Python runtime compatibility of the egg, as defined in
            the ``Python Tag`` section of PEP425.
        name : str
            The name of the egg.
        version : str
            The full version specification of the egg.

        """
        metadata = self.egg_metadata(python_tag, name, version)
        expected_sha256 = metadata['sha256']

        eggname = self._egg_name(name, version)
        path = self._egg_url(
            URLS.data.eggs.download, python_tag, name, version)
        return self._url_handler.iter_download(
            path, destination, expected_sha256, filename=eggname)

    def delete_egg(self, python_tag, name, version):
        """Delete an egg to the repository.

        Parameters
        ----------
        python_tag : str
            The Python runtime compatibility of the egg, as defined in
            the ``Python Tag`` section of PEP425.
        name : str
            The name of the egg.
        version : str
            The full version specification of the egg.

        """
        path = URLS.data.eggs.delete.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
            name=name,
            version=version,
            python_tag=python_tag,
        )
        return self._url_handler.delete(path)

    def upload_egg(self, filename, overwrite=False, enabled=True):
        """Upload an egg to the repository.

        """
        metadata = {'sha256': compute_sha256(filename)}
        path = URLS.data.eggs.upload.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
        )
        self._url_handler.upload(
            path, metadata, filename, overwrite=overwrite, enabled=enabled)

    def _egg_name(self, name, version):
        return '{0}-{1}.egg'.format(name, version)

    def _egg_url(self, base, python_tag, name, version):
        return base.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
            name=name,
            version=version,
            python_tag=python_tag,
        )

    #### Apps #################################################################

    def list_apps(self):
        """List all apps in a repository.

        """
        index = self.app_index()

        apps = [(app, '{0}-{1}'.format(version, build), python_tag)
                for python_tag, apps in index.items()
                for app, versions in apps.items()
                for version, builds in versions.items()
                for build, metadata in builds.items()]

        return apps

    def app_index(self):
        """Get the index of all apps in the current repository

        """
        index_path = (
            URLS.indices.apps.format(
                organization_name=self.organization_name,
                repository_name=self.repository_name,
                platform=self.name,
            )
        )

        return self._url_handler.get_json(index_path)

    def app_metadata(self, python_tag, app_id, version):
        """Download the metadata for an app.

        """
        path = URLS.metadata.artefacts.apps.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
            python_tag=python_tag,
            app_id=app_id,
            version=version,
        )
        return self._url_handler.get_json(path)

    #### Runtimes #############################################################

    def list_runtimes(self):
        """List all runtimes in a repository.

        """
        index = self.runtime_index()
        filenames = set(
            bdict['filename'] for language, ldict in index.items()
            for version, vdict in ldict.items()
            for build, bdict in vdict.items()
        )
        return list(filenames)

    def runtime_index(self):
        """Get the index of all the runtimes in the current repository

        """
        # FIXME: This works by downloading and parsing the index.  We
        # probably want to expose a list_runtimes endpoint in brood.
        index_path = URLS.indices.runtimes.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
        )
        return self._url_handler.get_json(index_path)

    def runtime_metadata(self, python_tag, version):
        """Fetch the metadata for a runtime.

        """
        path = self._runtime_url(
            URLS.metadata.artefacts.runtimes, python_tag, version)
        return self._url_handler.get_json(path)

    def download_runtime(self, python_tag, version, destination):
        """Download a runtime and save it in the given directory.

        """
        metadata = self.runtime_metadata(python_tag, version)
        expected_sha256 = metadata['sha256']

        path = self._runtime_url(
            URLS.data.runtimes.download, python_tag, version)
        self._url_handler.download_file(path, destination, expected_sha256)

    def iter_download_runtime(self, python_tag, version, destination):
        """Download a runtime and save it in the given directory.

        This method returns a tuple of (content_length, iterator).  The
        ``content_length`` is the total size of the download.  The
        ``iterator`` yield the size of each chunk as it is downloaded.

        """
        metadata = self.runtime_metadata(python_tag, version)
        expected_sha256 = metadata['sha256']

        path = self._runtime_url(
            URLS.data.runtimes.download, python_tag, version)
        return self._url_handler.iter_download(
            path, destination, expected_sha256)

    def _runtime_url(self, base, python_tag, version):
        return base.format(
            organization_name=self.organization_name,
            repository_name=self.repository_name,
            platform=self.name,
            python_tag=python_tag,
            version=version,
        )


class Repository(object):
    """A representation of a Brood repository.

    A repository contains artefacts for multiple platforms.  The
    ``Repository`` provides an entry-point to all platform data.

    """

    def __init__(self, organization_name, name, url_handler):
        """Create a Repository.

        """
        self.organization_name = organization_name
        self.name = name
        self._url_handler = url_handler

    def __repr__(self):
        return (
            '<{cls} organization={organization!r}, '
            'repository={repository!r}>'.format(
                cls=type(self).__name__,
                organization=self.organization_name,
                repository=self.name,
            )
        )

    def delete(self, force=False):
        """Delete this repository from Brood.

        """
        path = URLS.admin.repositories.format(
            organization_name=self.organization_name,
            repository_name=self.name,
        )
        self._url_handler.delete(path, force=force)

    def metadata(self):
        """Get the metadata for this repository.

        """
        raise NotImplementedError('Not implemented in brood.')

    def list_platforms(self):
        """Return a list of the names of all platforms supported by this
        repository.

        """
        raise NotImplementedError('Not implemented in brood.')

    def platform(self, platform_name):
        """Create and return a :class:`~.SinglePlatformRepository` to access
        artefacts.

        """
        return SinglePlatformRepository(
            repository=self,
            platform=platform_name,
            url_handler=self._url_handler,
        )

    # FIXME: This looks strange here, but the platform is specified in
    # metadata by the filename.
    def upload_runtime(self, filename, overwrite=False):
        """Upload a runtime.

        """
        metadata = RuntimeMetadata.from_file(filename)
        metadata_dict = {
            'language': metadata.language,
            'filename': metadata.filename,
            'build_system_version': metadata.build_system_version,
            'version': metadata.version,
            'file_format': metadata.file_format,
            'build': metadata.build,
            'sha256': metadata.sha256,
        }
        path = URLS.data.runtimes.upload.format(
            organization_name=self.organization_name,
            repository_name=self.name,
            platform=metadata.platform,
        )
        self._url_handler.upload(
            path, metadata_dict, filename, overwrite=overwrite)

    # FIXME: This looks strange here, but the platform is internal to
    # the metadata file.
    def upload_app(self, filename, overwrite=False):
        """Upload an app specification.

        """
        with open(filename, 'r') as fh:
            yaml_data = yaml.safe_load(fh)

        platform = yaml_data.get('platform')
        if platform is None:
            raise MissingPlatformError(
                'App yaml does not contain a platform specification')
        path = URLS.data.apps.upload.format(
            organization_name=self.organization_name,
            repository_name=self.name,
            platform=platform,
        )
        metadata = {
            'sha256': compute_sha256(filename),
        }
        self._url_handler.upload(path, metadata, filename, overwrite=overwrite)

    def reindex(self, eggs_to_enable):
        """Enable indexing of the listed eggs and re-index the repository.

        Parameters
        ----------
        eggs_to_enable : list
            List of filenames of eggs to enable.

        """
        # The platform string here is not used; it is provided to keep
        # Okonomiyaki happy.
        egg_specs = [
            LegacySpecDepend.from_egg(egg, 'win-32') for egg in eggs_to_enable
        ]
        eggs_to_enable = set(
            (spec.name, '{0}-{1}'.format(spec.version, spec.build),
             spec.python_tag)
            for spec in egg_specs)
        data = {
            'eggs': [
                {'name': name, 'version': version, 'python_tag': tag}
                for name, version, tag in eggs_to_enable
            ],
        }
        url = URLS.data.re_index.eggs.format(
            organization_name=self.organization_name,
            repository_name=self.name,
        )
        self._url_handler.post(url, data)
