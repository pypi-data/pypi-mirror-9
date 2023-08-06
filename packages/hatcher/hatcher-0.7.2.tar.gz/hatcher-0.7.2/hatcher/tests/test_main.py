from contextlib import contextmanager
from datetime import datetime
import hashlib
import json
import os
import re
import textwrap

import click
import requests
import responses
from click.testing import CliRunner
from mock import Mock, patch
from requests.exceptions import HTTPError, SSLError
from six.moves.urllib import parse
from tabulate import tabulate

from okonomiyaki.file_formats.egg import split_egg_name

from hatcher.core import brood_client
from hatcher.core import organization
from hatcher.core.auth import BroodBearerTokenAuth
from hatcher.core.brood_client import BroodClient as RealBroodClient
from hatcher.core.organization import Organization as RealOrganization
from hatcher.core.repository import (
    Repository as RealRepository,
    SinglePlatformRepository,
)
from hatcher.core.team import Team as RealTeam
from hatcher.core.url_templates import URLS
from hatcher.core.user import User as RealUser
from hatcher.errors import ChecksumMismatchError
from ..testing import unittest, make_testing_egg
from ..cli import main
from ..cli import repository_actions
from ..cli import team_actions
from ..cli import utils


patch_brood_client = patch.object(utils, 'BroodClient')
patch_organization = patch.object(brood_client, 'Organization')
patch_repository = patch.object(organization, 'Repository')
patch_team = patch.object(organization, 'Team')
patch_user = patch.object(organization, 'User')


class TestingException(Exception):
    pass


class MainTestingMixin(object):

    def setUp(self):
        self.runner = CliRunner()
        self.organization = 'acme'
        self.repository = 'dev'
        self.team = 'dev-team'
        self.platform = 'rh5-64'
        self.user = 'user@acme.org'

    def _mock_brood_client_class(self, BroodClient):
        BroodClient.return_value = brood_client = Mock(
            spec=RealBroodClient)
        BroodClient.from_url.return_value = brood_client
        brood_client.organization.return_value = Mock(
            spec=RealOrganization)
        return brood_client

    def _mock_organization_class(self, Organization):
        Organization.return_value = organization = Mock(spec=RealOrganization)
        organization.repository.return_value = Mock(
            spec=RealRepository)
        organization.team.return_value = Mock(spec=RealTeam)
        return organization

    def _mock_repository_class(self, Repository):
        Repository.return_value = repo = Mock(spec=RealRepository)
        repo.organization_name = self.organization
        repo.name = self.repository
        repo.platform.return_value = platform_repo = Mock(
            spec=SinglePlatformRepository)
        return repo, platform_repo

    def _mock_team_class(self, Team):
        Team.return_value = team = Mock(spec=RealTeam)
        team.name = self.team
        return team

    def _mock_user_class(self, User):
        User.return_value = user = Mock(spec=RealUser)
        user.email = self.user
        return user

    def assertOrganizationConstructedCorrectly(self, Organization):
        self.assertEqual(Organization.call_count, 1)
        self.assertEqual(
            Organization.call_args[0],
            (self.organization,),
        )
        self.assertIn('url_handler', Organization.call_args[1])

    def assertRepositoryConstructedCorrectly(self, Repository):
        self.assertEqual(Repository.call_count, 1)
        self.assertEqual(
            Repository.call_args[0],
            (self.organization, self.repository),
        )
        self.assertIn('url_handler', Repository.call_args[1])

    def assertTeamConstructedCorrectly(self, Team):
        self.assertEqual(Team.call_count, 1)
        self.assertEqual(
            Team.call_args[0],
            (self.organization, self.team),
        )
        self.assertIn('url_handler', Team.call_args[1])

    def assertUserConstructedCorrectly(self, User):
        self.assertEqual(User.call_count, 1)
        self.assertEqual(
            User.call_args[0],
            (self.organization, self.user),
        )
        self.assertIn('url_handler', User.call_args[1])


class TestBasic(MainTestingMixin, unittest.TestCase):
    def _get_brood_client_proxy(self, args=()):
        # Given
        out = []

        @main.hatcher.command('get-ctx')
        @click.pass_context
        def get_ctx(ctx):
            out.append(ctx.obj)

        # When
        CliRunner().invoke(
            main.hatcher,
            args=['-u', 'http://brood-dev'] + list(args) + ['get-ctx'],
        )

        self.assertEqual(len(out), 1)
        proxy, = out
        return proxy

    def test_brood_client_proxy(self):
        # Given
        proxy = self._get_brood_client_proxy()

        # Then
        self.assertIsInstance(proxy, utils.BroodClientProxy)
        self.assertTrue(proxy.verify_ssl)
        # realize brood_client
        proxy.organization
        brood_client = proxy.brood_client
        self.assertIsInstance(brood_client, RealBroodClient)
        url_handler = brood_client._url_handler
        self.assertTrue(url_handler.verify_ssl)
        self.assertTrue(url_handler._session.verify)

    def test_insecure_option(self):
        # Given
        proxy = self._get_brood_client_proxy(['--insecure'])

        # Then
        self.assertIsInstance(proxy, utils.BroodClientProxy)
        self.assertFalse(proxy.verify_ssl)
        # realize brood_client
        proxy.organization
        brood_client = proxy.brood_client
        self.assertIsInstance(brood_client, RealBroodClient)
        url_handler = brood_client._url_handler
        self.assertFalse(url_handler.verify_ssl)
        self.assertFalse(url_handler._session.verify)

    def test_print_command_tree(self):
        # When
        result = CliRunner().invoke(main.hatcher, args=['--command-tree'])

        # Then
        self.assertTrue(result.output.startswith('hatcher'))
        self.assertIn('[OPTIONS]', result.output)
        self.assertEqual(result.exit_code, 0)

    def test_url_required(self):
        # Given
        args = ['teams', 'list', 'enthought']

        # When
        result = CliRunner().invoke(main.hatcher, args=args)

        # Then
        self.assertRegexpMatches(result.output, r'Missing option.*?--url')
        self.assertEqual(result.exit_code, 2)

    def test_help_without_url_argument(self):
        # Given
        args = ['teams', 'list', 'enthought', '--help']

        # When
        result = CliRunner().invoke(main.hatcher, args=args)

        # Then
        self.assertRegexpMatches(
            result.output, team_actions.list_teams.help.strip())
        self.assertEqual(result.exit_code, 0)

    def test_no_auth(self):
        # Given
        self.auth = object()

        @main.hatcher.command()
        @utils.pass_brood_client
        def dummy(brood_client):
            self.auth = brood_client._url_handler._session.auth

        # When
        result = CliRunner().invoke(
            main.hatcher, args=['-u', 'brood-dev', 'dummy'])

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(self.auth, None)

    def test_auth_username_password(self):
        # Given
        username = 'user'
        password = 'password'

        self.auth = None

        @main.hatcher.command()
        @utils.pass_brood_client
        def dummy(brood_client):
            self.auth = brood_client._url_handler._session.auth

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'brood-dev', '-U', username, '-p', password, 'dummy'])

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(self.auth, (username, password))

    def test_auth_username_no_password(self):
        # Given
        username = 'user'
        password = 'password'

        self.auth = None

        @main.hatcher.command()
        @utils.pass_brood_client
        def dummy(brood_client):
            self.auth = brood_client._url_handler._session.auth

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'brood-dev', '-U', username, 'dummy'],
            input=password,
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(self.auth, (username, password))

    def test_auth_token(self):
        # Given
        token = 'token'

        self.auth = None

        @main.hatcher.command()
        @utils.pass_brood_client
        def dummy(brood_client):
            self.auth = brood_client._url_handler._session.auth

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'brood-dev', '-t', token, 'dummy'],
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertIsInstance(self.auth, BroodBearerTokenAuth)
        self.assertEqual(self.auth.token, token)

    def test_auth_token_and_password(self):
        # Given
        password = 'password'

        @main.hatcher.command()
        @utils.pass_brood_client
        def dummy(brood_client):
            pass

        # When
        result = CliRunner().invoke(
            main.hatcher, args=['-u', 'brood-dev', '-p', password,
                                '-t', 'token', 'dummy'])

        # Then
        self.assertEqual(result.exit_code, 2)
        self.assertRegexpMatches(
            result.output, r'.*?Password provided with no username$')

    def test_auth_token_and_username(self):
        # Given
        username = 'user'
        password = 'password'

        self.auth = None

        @main.hatcher.command()
        @utils.pass_brood_client
        def dummy(brood_client):
            self.auth = brood_client._url_handler._session.auth

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'brood-dev', '-U', username, '-t', 'token', 'dummy'],
            input=password,
        )

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(self.auth, (username, password))

    def test_auth_password_no_username(self):
        # Given
        password = 'password'

        @main.hatcher.command()
        @utils.pass_brood_client
        def dummy(brood_client):
            pass

        # When
        result = CliRunner().invoke(
            main.hatcher, args=['-u', 'brood-dev', '-p', password, 'dummy'])

        # Then
        self.assertEqual(result.exit_code, 2)
        self.assertRegexpMatches(
            result.output, r'.*?Password provided with no username$')

    def test_debug_flag_unset(self):
        # Given
        @main.hatcher.command()
        @utils.pass_brood_client
        def dummy(brood_client):
            raise TestingException()

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'brood-dev', '-U', 'username', '-p', 'none',
                  '-t', 'token', 'dummy'],
        )

        # Then
        self.assertEqual(result.exit_code, -1)
        self.assertRegexpMatches(result.output, 'Unexpected error')
        self.assertIsInstance(result.exception, SystemExit)

    def test_debug_flag_set(self):
        # Given
        @main.hatcher.command()
        @utils.pass_brood_client
        def dummy(brood_client):
            raise TestingException()

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', 'brood-dev', '--debug', '-U', 'username', '-p', 'none',
                  '-t', 'token', 'dummy'],
        )

        # Then
        self.assertEqual(result.exit_code, -1)
        self.assertIsInstance(result.exception, TestingException)

    @responses.activate
    def test_ssl_error(self):
        # Given
        host = 'https://brood-dev'
        url = '{host}{uri}'.format(
            host=host,
            uri=URLS.indices.apps.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )

        def ssl_callback(request):
            raise SSLError(None, request=request)

        responses.add_callback(responses.GET, url,
                               callback=ssl_callback)

        @main.hatcher.command()
        @utils.pass_brood_client
        def dummy(brood_client):
            raise requests.get(url)

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['-u', host, '-U', 'username', '-p', 'none',
                  '-t', 'token', 'dummy'],
        )

        # Then
        self.assertEqual(result.exit_code, -1)
        expected = ('To connect to {} insecurely, pass the '
                    '`--insecure` flag'.format(host))
        self.assertRegexpMatches(result.output, expected)
        self.assertIsInstance(result.exception, SystemExit)

    @responses.activate
    def test_ssl_error_debug(self):
        # Given
        host = 'https://brood-dev'
        url = '{host}{uri}'.format(
            host=host,
            uri=URLS.indices.apps.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )

        def ssl_callback(request):
            raise SSLError(None, request=request)

        responses.add_callback(responses.GET, url,
                               callback=ssl_callback)

        @main.hatcher.command()
        @utils.pass_brood_client
        def dummy(brood_client):
            raise requests.get(url)

        # When
        result = CliRunner().invoke(
            main.hatcher,
            args=['--debug', '-u', host, '-U', 'username', '-p', 'none',
                  '-t', 'token', 'dummy'],
        )

        # Then
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(result.output, '')
        self.assertIsInstance(result.exception, SSLError)


class UploadEggResult(object):
    def __init__(self, testing_egg):
        self.testing_egg = testing_egg
        self.result = None

    @property
    def filename(self):
        return self.testing_egg.path


class TestUploadEggMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.host = 'http://brood-dev.invalid'
        self.initial_args = ['--url', self.host, 'eggs', 'upload']
        self.final_args = [self.organization, self.repository, self.platform]

    def _upload_egg(self, metadata=None, force=False, verify=False,
                    debug=False):
        with self._upload_egg_context(
                metadata=metadata,
                force=force,
                verify=verify,
                debug=debug) as result:
            pass
        return result.filename, result.result

    @contextmanager
    def _upload_egg_context(self, metadata=None, force=False, verify=False,
                            debug=False):
        if metadata is None:
            metadata = {}
        initial_args = self.initial_args
        if force:
            initial_args = initial_args + ['--force']
        if verify:
            initial_args = initial_args + ['--verify']
        if debug:
            initial_args = ['--debug'] + initial_args

        with self.runner.isolated_filesystem() as tempdir:
            testing_egg = make_testing_egg(tempdir, **metadata)
            result = UploadEggResult(testing_egg)
            yield result
            result.result = self.runner.invoke(
                main.hatcher,
                args=initial_args + self.final_args + [testing_egg.path],
            )

    @patch_repository
    def test_without_force(self, Repository):
        # Given
        repository, platform_repo = self._mock_repository_class(Repository)
        upload_egg = platform_repo.upload_egg

        # When
        filename, result = self._upload_egg(force=False)

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        repository.platform.assert_called_once_with(self.platform)
        upload_egg.assert_called_once_with(filename, overwrite=False)
        self.assertEqual(result.exit_code, 0)

    @patch_repository
    def test_with_force(self, Repository):
        # Given
        repository, platform_repo = self._mock_repository_class(Repository)
        upload_egg = platform_repo.upload_egg

        # When
        filename, result = self._upload_egg(force=True)

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        repository.platform.assert_called_once_with(self.platform)
        upload_egg.assert_called_once_with(filename, overwrite=True)
        self.assertEqual(result.exit_code, 0)

    @responses.activate
    def test_upload_no_verify(self):
        # Given
        metadata = {
            'name': 'nose',
            'version': '1.3.0',
            'build': 1,
            'python': '2.7'
        }

        upload_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.data.eggs.upload.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )
        responses.add(
            responses.POST,
            upload_url,
            status=200,
        )

        # When
        filename, result = self._upload_egg(metadata=metadata)

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(responses.calls), 1)
        upload_request, = responses.calls

        parsed = parse.urlsplit(upload_request.request.url)
        used_upload_url = parse.urlunsplit(parsed[:3] + ('', ''))
        self.assertEqual(used_upload_url, upload_url)

    @responses.activate
    def test_upload_verify_no_upstream(self):
        # Given
        metadata = {
            'name': 'nose',
            'version': '1.3.0',
            'build': 1,
            'python': '2.7'
        }

        metadata_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.metadata.artefacts.eggs.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag='cp27',
                name='nose',
                version='1.3.0-1',
            ),
        )
        responses.add(
            responses.GET,
            metadata_url,
            status=404,
        )

        upload_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.data.eggs.upload.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )
        responses.add(
            responses.POST,
            upload_url,
            status=200,
        )

        # When
        filename, result = self._upload_egg(metadata=metadata, verify=True)

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(responses.calls), 2)
        metadata_request, upload_request = responses.calls
        self.assertEqual(metadata_request.request.url, metadata_url)

        parsed = parse.urlsplit(upload_request.request.url)
        used_upload_url = parse.urlunsplit(parsed[:3] + ('', ''))
        self.assertEqual(used_upload_url, upload_url)

    @responses.activate
    def test_upload_verify_invalid(self):
        # Given
        metadata = {
            'name': 'nose',
            'version': '1.3.0',
            'build': 1,
            'python': '2.7'
        }
        server_metadata = {
            'sha256': 'abc123',
        }

        metadata_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.metadata.artefacts.eggs.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag='cp27',
                name='nose',
                version='1.3.0-1',
            ),
        )
        responses.add(
            responses.GET,
            metadata_url,
            content_type='application/json',
            status=200,
            body=json.dumps(server_metadata),
        )

        # When
        filename, result = self._upload_egg(
            metadata=metadata, verify=True, debug=True)

        # Then
        self.assertEqual(result.exit_code, -1)
        self.assertIsInstance(result.exception, ChecksumMismatchError)
        self.assertEqual(len(responses.calls), 1)
        metadata_request, = responses.calls
        self.assertEqual(metadata_request.request.url, metadata_url)

    @responses.activate
    def test_upload_verify_error(self):
        # Given
        metadata = {
            'name': 'nose',
            'version': '1.3.0',
            'build': 1,
            'python': '2.7'
        }
        error = 'an error occurred'

        metadata_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.metadata.artefacts.eggs.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag='cp27',
                name='nose',
                version='1.3.0-1',
            ),
        )
        responses.add(
            responses.GET,
            metadata_url,
            content_type='application/json',
            status=400,
            body=json.dumps({'error': error}),
        )

        # When
        filename, result = self._upload_egg(metadata=metadata, verify=True)

        # Then
        self.assertEqual(result.exit_code, -1)
        self.assertIsInstance(result.exception, SystemExit)
        self.assertEqual(len(responses.calls), 1)
        metadata_request, = responses.calls
        self.assertEqual(metadata_request.request.url, metadata_url)

    @responses.activate
    def test_upload_verify_valid(self):
        # Given
        metadata = {
            'name': 'nose',
            'version': '1.3.0',
            'build': 1,
            'python': '2.7'
        }
        metadata_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.metadata.artefacts.eggs.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag='cp27',
                name='nose',
                version='1.3.0-1',
            ),
        )

        # When
        with self._upload_egg_context(
                metadata=metadata, verify=True) as upload_result:
            server_metadata = {
                'sha256': upload_result.testing_egg.sha256,
            }

            responses.add(
                responses.GET,
                metadata_url,
                content_type='application/json',
                status=200,
                body=json.dumps(server_metadata),
            )
        result = upload_result.result

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(responses.calls), 1)
        metadata_request, = responses.calls
        self.assertEqual(metadata_request.request.url, metadata_url)


class TestBatchUploadEggsMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.host = 'http://brood-dev.invalid'
        self.initial_args = ['--url', self.host, 'eggs', 'batch-upload']
        self.final_args = [self.organization, self.repository, self.platform]
        self.files = ['nose-1.3.0-1.egg', 'numpy-1.8.0-1.egg']
        self.upload_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.data.eggs.upload.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )

    def _batch_upload_eggs(self, force=False, debug=False):
        initial_args = self.initial_args
        if force:
            initial_args = initial_args + ['--force']
        if debug:
            initial_args = ['--debug'] + initial_args
        with self.runner.isolated_filesystem() as tempdir:
            for filename in self.files:
                name, version, build = split_egg_name(filename)
                make_testing_egg(
                    tempdir, name=name, version=version, build=build)
            result = self.runner.invoke(
                main.hatcher,
                args=initial_args + self.final_args + self.files,
            )

        return result

    def _metadata_url_from_file(self, filename):
        name, version, build = split_egg_name(filename)
        return '{host}{uri}'.format(
            host=self.host,
            uri=URLS.metadata.artefacts.eggs.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag='cp27',
                name=name,
                version='{}-{}'.format(version, build),
            ),
        )

    @patch.object(repository_actions, 'progress')
    @responses.activate
    def test_batch_upload_non_existing_file(self, progress):
        # Given
        progress.bar = lambda files: files
        r_error = ('Error: Invalid value for "eggs": Path '
                   '"foo-1.1.0-1.egg" does not exist.')

        # When
        result = self.runner.invoke(
            main.hatcher,
            args=self.initial_args + self.final_args + ["foo-1.1.0-1.egg"],
        )

        # Then
        self.assertEqual(result.exit_code, 2)
        self.assertRegexpMatches(result.output, re.escape(r_error))

    @patch.object(repository_actions, 'progress')
    @responses.activate
    def test_batch_upload_directory_fails(self, progress):
        # Given
        progress.bar = lambda files: files
        r_error_template = ('Error: Invalid value for "eggs": Path '
                            '"{}" is a directory.')

        # When
        with self.runner.isolated_filesystem() as tempdir:
            result = self.runner.invoke(
                main.hatcher,
                args=self.initial_args + self.final_args + [tempdir],
            )

        # Then
        self.assertEqual(result.exit_code, 2)
        self.assertRegexpMatches(result.output,
                                 re.escape(r_error_template.format(tempdir)))

    @patch.object(repository_actions, 'progress')
    @responses.activate
    def test_batch_upload_defaults_no_existing(self, progress):
        # Given
        progress.bar = lambda files: files
        metadata_urls = [self._metadata_url_from_file(filename)
                         for filename in self.files]

        def metadata_callback(request):
            return (404, {}, '{"error": "not found"}')

        for url in metadata_urls:
            responses.add_callback(
                responses.GET,
                url,
                metadata_callback,
            )

        responses.add(
            responses.POST,
            self.upload_url,
            status=200,
        )

        reindex_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.data.re_index.eggs.format(
                organization_name=self.organization,
                repository_name=self.repository,
            ),
        )
        responses.add(
            responses.POST,
            reindex_url,
            status=200,
        )

        # When
        result = self._batch_upload_eggs(force=False, debug=True)

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(responses.calls), 5)
        (metadata_request1, upload_request1, metadata_request2,
         upload_request2, reindex_request) = responses.calls

        # Both eggs have their metadata queried
        self.assertNotEqual(metadata_request1.request.url,
                            metadata_request2.request.url)

        # The upload URL is always the same
        self.assertEqual(upload_request1.request.url,
                         upload_request2.request.url)
        self.assertIn(metadata_request1.request.url, metadata_urls)
        parsed = parse.urlsplit(upload_request1.request.url)
        used_upload_url = parse.urlunsplit(parsed[:3] + ('', ''))
        self.assertEqual(used_upload_url, self.upload_url)

        self.assertEqual(reindex_request.request.url, reindex_url)

        # No console output
        self.assertEqual(result.output, '')

    @patch.object(repository_actions, 'progress')
    @responses.activate
    def test_batch_reindex_error(self, progress):
        # Given
        progress.bar = lambda files: files
        metadata_urls = [self._metadata_url_from_file(filename)
                         for filename in self.files]

        def metadata_callback(request):
            return (404, {}, '{"error": "not found"}')

        for url in metadata_urls:
            responses.add_callback(
                responses.GET,
                url,
                metadata_callback,
            )

        responses.add(
            responses.POST,
            self.upload_url,
            status=200,
        )

        reindex_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.data.re_index.eggs.format(
                organization_name=self.organization,
                repository_name=self.repository,
            ),
        )
        responses.add(
            responses.POST,
            reindex_url,
            status=400,
            content_type='application/json',
            body=json.dumps({'error': 'failed'})
        )

        # When
        result = self._batch_upload_eggs(force=False, debug=True)

        # Then
        self.assertEqual(result.exit_code, -1)
        self.assertIsInstance(result.exception, HTTPError)
        self.assertEqual(len(responses.calls), 5)
        (metadata_request1, upload_request1, metadata_request2,
         upload_request2, reindex_request) = responses.calls

        # Both eggs have their metadata queried
        self.assertNotEqual(metadata_request1.request.url,
                            metadata_request2.request.url)

        # The upload URL is always the same
        self.assertEqual(upload_request1.request.url,
                         upload_request2.request.url)
        self.assertIn(metadata_request1.request.url, metadata_urls)
        parsed = parse.urlsplit(upload_request1.request.url)
        used_upload_url = parse.urlunsplit(parsed[:3] + ('', ''))
        self.assertEqual(used_upload_url, self.upload_url)

        self.assertEqual(reindex_request.request.url, reindex_url)

        # No console output (handled by generic error handler)
        self.assertFalse(result.output, '')

    @patch.object(repository_actions, 'progress')
    @responses.activate
    def test_with_error(self, progress):
        # Given
        progress.bar = lambda files: files
        metadata_urls = [self._metadata_url_from_file(filename)
                         for filename in self.files]

        def metadata_callback(request):
            return (404, {}, '{"error": "not found"}')

        for url in metadata_urls:
            responses.add_callback(
                responses.GET,
                url,
                metadata_callback,
            )

        responses.add(
            responses.POST,
            self.upload_url,
            status=400,
            content_type='application/json',
            body=json.dumps({'error': "can't do that!"})
        )

        # When
        result = self._batch_upload_eggs(force=False, debug=True)

        # Then
        self.assertEqual(result.exit_code, -1)
        self.assertIsInstance(result.exception, HTTPError)
        self.assertEqual(len(responses.calls), 2)
        metadata_request, upload_request = responses.calls
        self.assertIn(metadata_request.request.url, metadata_urls)

        self.assertEqual(upload_request.response.status_code, 400)
        parsed = parse.urlsplit(upload_request.request.url)
        used_upload_url = parse.urlunsplit(parsed[:3] + ('', ''))
        self.assertEqual(used_upload_url, self.upload_url)

        # Console output for errors
        regexp = '|'.join(['({})'.format(re.escape(path)) for path in
                           self.files])

        self.assertRegexpMatches(
            result.output.strip(), r'^Error uploading {}$'.format(regexp))

    @patch.object(repository_actions, 'progress')
    @responses.activate
    def test_batch_upload_force(self, progress):
        # Given
        progress.bar = lambda files: files

        responses.add(
            responses.POST,
            self.upload_url,
            status=200,
        )

        reindex_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.data.re_index.eggs.format(
                organization_name=self.organization,
                repository_name=self.repository,
            ),
        )
        responses.add(
            responses.POST,
            reindex_url,
            status=200,
        )

        # When
        result = self._batch_upload_eggs(force=True, debug=True)

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(responses.calls), 3)
        upload_request1, upload_request2, reindex_request = responses.calls

        # The upload URL is always the same
        self.assertEqual(upload_request1.request.url,
                         upload_request2.request.url)
        parsed = parse.urlsplit(upload_request1.request.url)
        used_upload_url = parse.urlunsplit(parsed[:3] + ('', ''))
        self.assertEqual(used_upload_url, self.upload_url)

        self.assertEqual(reindex_request.request.url, reindex_url)

        # No console output
        self.assertEqual(result.output, '')

    @patch.object(repository_actions, 'progress')
    @responses.activate
    def test_batch_upload_force_error(self, progress):
        # Given
        progress.bar = lambda files: files

        responses.add(
            responses.POST,
            self.upload_url,
            status=400,
            content_type='application/json',
            body=json.dumps({'error': "can't do that!"})
        )

        # When
        result = self._batch_upload_eggs(force=True, debug=True)

        # Then
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(len(responses.calls), 1)
        upload_request1, = responses.calls

        # The upload URL is always the same
        parsed = parse.urlsplit(upload_request1.request.url)
        used_upload_url = parse.urlunsplit(parsed[:3] + ('', ''))
        self.assertEqual(used_upload_url, self.upload_url)

        # Console output for errors
        regexp = '|'.join(['({})'.format(re.escape(path)) for path in
                           self.files])

        self.assertRegexpMatches(
            result.output.strip(), r'^Error uploading {}$'.format(regexp))


class TestDownloadEggMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.initial_args = ['--url', 'brood-dev.invalid', 'eggs', 'download']
        self.final_args = [
            self.organization, self.repository, self.platform]

    @patch_repository
    def test_download(self, Repository):
        # Given
        args = ['nose', '1.3.0-1', 'cp27', 'destination']
        repository, platform_repo = self._mock_repository_class(Repository)
        iter_download_egg = platform_repo.iter_download_egg
        iter_download_egg.return_value = 0, []

        # When
        result = self.runner.invoke(
            main.hatcher,
            args=self.initial_args + self.final_args + args,
        )

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        iter_download_egg.assert_called_once_with(*args)
        self.assertEqual(result.exit_code, 0)

    @patch_repository
    def test_download_checksum_mismatch(self, Repository):
        # Given
        error_text = 'Checksum mismatch on download'

        def iter_download():
            yield 0
            raise ChecksumMismatchError(error_text)

        args = ['nose', '1.3.0-1', 'cp27', 'destination']
        repository, platform_repo = self._mock_repository_class(Repository)
        iter_download_egg = platform_repo.iter_download_egg
        iter_download_egg.return_value = 0, iter_download()

        # When
        result = self.runner.invoke(
            main.hatcher,
            args=self.initial_args + self.final_args + args,
        )

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(result.output.strip(), error_text)
        self.assertIsInstance(result.exception, SystemExit)
        iter_download_egg.assert_called_once_with(*args)

    @patch_repository
    def test_download_checksum_mismatch_debug(self, Repository):
        # Given
        error_text = 'Checksum mismatch on download'

        def iter_download():
            yield 0
            raise ChecksumMismatchError(error_text)

        args = ['nose', '1.3.0-1', 'cp27', 'destination']
        repository, platform_repo = self._mock_repository_class(Repository)
        iter_download_egg = platform_repo.iter_download_egg
        iter_download_egg.return_value = 0, iter_download()

        # When
        result = self.runner.invoke(
            main.hatcher,
            args=['--debug'] + self.initial_args + self.final_args + args,
        )

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(result.output.strip(), '')
        self.assertIsInstance(result.exception, ChecksumMismatchError)
        iter_download_egg.assert_called_once_with(*args)


class TestEggMetadataMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.host = 'http://brood-dev.invalid'
        self.initial_args = ['--url', self.host, 'eggs', 'metadata']
        self.python_tag = 'none'
        self.final_args = [
            self.organization, self.repository, self.platform, self.python_tag]

    @patch('requests.Session')
    def test_egg_metadata(self, Session):
        # Given
        expected = {
            'filename': 'MKL-10.3-1.egg',
            'name': 'mkl',
            'egg_basename': 'MKL',
            'version': '10.3',
            'build': 1,
            'full_version': '10.3-1',
            'packages': [],
            'md5': 'abc1234',
            'sha256': 'abc1234def456',
            'python_tag': None,
            'python': None,
            'product': None,
            'size': 12345,
            'type': 'egg',
            'enabled': True
        }
        session = Session.return_value = Mock()
        session.headers = {}
        get = session.get = Mock()
        response = get.return_value = Mock()
        response_json = response.json = Mock()
        response_json.return_value = expected.copy()

        expected_url = '{host}{url}'.format(
            host=self.host,
            url=URLS.metadata.artefacts.eggs.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag=self.python_tag,
                name='mkl',
                version='10.3-1',
            ),
        )

        # When
        result = self.runner.invoke(
            main.hatcher,
            args=self.initial_args + self.final_args + ['mkl', '10.3-1'],
        )

        # Then
        Session.assert_called_once_with()
        get.assert_called_once_with(expected_url)
        response_json.assert_called_once_with()

        self.assertEqual(json.loads(result.output), expected)
        self.assertEqual(result.exit_code, 0)


class TestRuntimeMetadataMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.initial_args = ['--url', 'brood-dev.invalid', 'runtimes',
                             'metadata']
        self.final_args = [self.organization, self.repository, 'rh5-64',
                           'cp27', '2.7.3-1']

    @patch_repository
    def test_runtime_metadata(self, Repository):
        # Given
        expected = {
            'language': 'python',
            'version': '2.7.3',
            'build': 1,
        }
        repository, platform_repo = self._mock_repository_class(Repository)
        runtime_metadata = platform_repo.runtime_metadata
        runtime_metadata.return_value = expected

        # When
        result = self.runner.invoke(
            main.hatcher,
            args=self.initial_args + self.final_args,
        )

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        runtime_metadata.assert_called_once_with('cp27', '2.7.3-1')
        self.assertEqual(json.loads(result.output), expected)
        self.assertEqual(result.exit_code, 0)


class TestUploadRuntimeMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.host = host = 'http://brood-dev.invalid'
        self.initial_args = ['--url', host, 'runtimes', 'upload']
        self.final_args = [self.organization, self.repository]

    def _upload_runtime(self, filename=None, data=None, force=False,
                        verify=False, debug=False):
        if data is None:
            data = 'data'
        if filename is None:
            filename = 'python_runtime_2.7.3_2.0.0_rh5-64_1.zip'
        initial_args = self.initial_args
        if force:
            initial_args = initial_args + ['--force']
        if verify:
            initial_args = initial_args + ['--verify']
        if debug:
            initial_args = ['--debug'] + initial_args
        with self.runner.isolated_filesystem() as tempdir:
            filename = os.path.join(tempdir, filename)
            with open(filename, 'w') as fh:
                fh.write(data)

            result = self.runner.invoke(
                main.hatcher,
                args=initial_args + self.final_args + [filename],
            )

        return filename, result

    @patch_repository
    def test_without_force(self, Repository):
        # Given
        repository, platform_repo = self._mock_repository_class(Repository)
        upload_runtime = repository.upload_runtime

        # When
        filename, result = self._upload_runtime(force=False)

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        upload_runtime.assert_called_once_with(filename, overwrite=False)
        self.assertEqual(result.exit_code, 0)

    @patch_repository
    def test_with_force(self, Repository):
        # Given
        repository, platform_repo = self._mock_repository_class(Repository)
        upload_runtime = repository.upload_runtime

        # When
        filename, result = self._upload_runtime(force=True)

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        upload_runtime.assert_called_once_with(filename, overwrite=True)
        self.assertEqual(result.exit_code, 0)

    @responses.activate
    def test_upload_no_verify(self):
        # Given
        upload_filename = 'python_runtime_2.7.6_2.0.0_rh5-64_1.zip'
        data = 'runtime_content'

        upload_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.data.runtimes.upload.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )
        responses.add(
            responses.POST,
            upload_url,
            status=200,
        )

        # When
        filename, result = self._upload_runtime(
            filename=upload_filename, data=data)

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(responses.calls), 1)
        upload_request, = responses.calls

        parsed = parse.urlsplit(upload_request.request.url)
        used_upload_url = parse.urlunsplit(parsed[:3] + ('', ''))
        self.assertEqual(used_upload_url, upload_url)

    @responses.activate
    def test_upload_verify_no_upstream(self):
        # Given
        upload_filename = 'python_runtime_2.7.6_2.0.0_rh5-64_1.zip'
        data = 'runtime_content'

        metadata_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.metadata.artefacts.runtimes.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag='cp27',
                version='2.7.6-1',
            ),
        )
        responses.add(
            responses.GET,
            metadata_url,
            status=404,
        )

        upload_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.data.runtimes.upload.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
            ),
        )
        responses.add(
            responses.POST,
            upload_url,
            status=200,
        )

        # When
        filename, result = self._upload_runtime(
            filename=upload_filename, data=data, verify=True)

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(responses.calls), 2)
        metadata_request, upload_request = responses.calls
        self.assertEqual(metadata_request.request.url, metadata_url)

        parsed = parse.urlsplit(upload_request.request.url)
        used_upload_url = parse.urlunsplit(parsed[:3] + ('', ''))
        self.assertEqual(used_upload_url, upload_url)

    @responses.activate
    def test_upload_verify_valid(self):
        # Given
        upload_filename = 'python_runtime_2.7.6_2.0.0_rh5-64_1.zip'
        data = 'runtime_content'
        sha256 = hashlib.sha256(data.encode('ascii')).hexdigest()
        server_metadata = {
            'sha256': sha256,
        }

        metadata_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.metadata.artefacts.runtimes.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag='cp27',
                version='2.7.6-1',
            ),
        )
        responses.add(
            responses.GET,
            metadata_url,
            content_type='application/json',
            status=200,
            body=json.dumps(server_metadata),
        )

        # When
        filename, result = self._upload_runtime(
            filename=upload_filename, data=data, verify=True)

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(len(responses.calls), 1)
        metadata_request, = responses.calls
        self.assertEqual(metadata_request.request.url, metadata_url)

    @responses.activate
    def test_upload_verify_checksum_failure(self):
        # Given
        upload_filename = 'python_runtime_2.7.6_2.0.0_rh5-64_1.zip'
        data = 'runtime_content'
        server_metadata = {
            'sha256': 'invalid sha256',
        }

        metadata_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.metadata.artefacts.runtimes.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag='cp27',
                version='2.7.6-1',
            ),
        )
        responses.add(
            responses.GET,
            metadata_url,
            content_type='application/json',
            status=200,
            body=json.dumps(server_metadata),
        )

        # When
        ## Use --debug so that we can assert on the actual exception
        ## raised rather than a SystemExit from the Exception handler
        filename, result = self._upload_runtime(
            filename=upload_filename, data=data, verify=True, debug=True)

        # Then
        self.assertIsInstance(result.exception, ChecksumMismatchError)
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(len(responses.calls), 1)
        metadata_request, = responses.calls
        self.assertEqual(metadata_request.request.url, metadata_url)

    @responses.activate
    def test_upload_verify_error(self):
        # Given
        upload_filename = 'python_runtime_2.7.6_2.0.0_rh5-64_1.zip'
        data = 'runtime_content'
        error = 'An error'

        metadata_url = '{host}{uri}'.format(
            host=self.host,
            uri=URLS.metadata.artefacts.runtimes.format(
                organization_name=self.organization,
                repository_name=self.repository,
                platform=self.platform,
                python_tag='cp27',
                version='2.7.6-1',
            ),
        )
        responses.add(
            responses.GET,
            metadata_url,
            content_type='application/json',
            status=400,
            body=json.dumps({'error': error})
        )

        # When
        filename, result = self._upload_runtime(
            filename=upload_filename, data=data, verify=True)

        # Then
        self.assertIsInstance(result.exception, SystemExit)
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(result.output.strip(), error)
        self.assertEqual(len(responses.calls), 1)
        metadata_request, = responses.calls
        self.assertEqual(metadata_request.request.url, metadata_url)


class TestDownloadRuntimeMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.initial_args = ['--url', 'brood-dev.invalid', 'runtimes',
                             'download']
        self.final_args = [self.organization, self.repository, self.platform]

    @patch_repository
    def test_download(self, Repository):
        # Given
        args = ['cp27', '2.7.3-1', 'destination']
        repository, platform_repo = self._mock_repository_class(Repository)
        iter_download_runtime = platform_repo.iter_download_runtime
        iter_download_runtime.return_value = 0, []

        # When
        result = self.runner.invoke(
            main.hatcher,
            args=self.initial_args + self.final_args + args,
        )

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        iter_download_runtime.assert_called_once_with(*args)
        self.assertEqual(result.exit_code, 0)


class TestUploadAppMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.initial_args = ['--url', 'brood-dev.invalid', 'apps', 'upload']
        self.final_args = [self.organization, self.repository]

    def _upload_app(self, force=False):
        if force:
            initial_args = self.initial_args + ['--force']
        else:
            initial_args = self.initial_args
        with self.runner.isolated_filesystem() as tempdir:
            filename = os.path.join(tempdir, 'mayavi.app')
            with open(filename, 'w') as fh:
                fh.write('data')

            result = self.runner.invoke(
                main.hatcher,
                args=initial_args + self.final_args + [filename],
            )

        return filename, result

    @patch_repository
    def test_without_force(self, Repository):
        # Given
        repository, platform_repo = self._mock_repository_class(Repository)
        upload_app = repository.upload_app

        # When
        filename, result = self._upload_app(force=False)

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        upload_app.assert_called_once_with(filename, overwrite=False)
        self.assertEqual(result.exit_code, 0)

    @patch_repository
    def test_with_force(self, Repository):
        # Given
        repository, platform_repo = self._mock_repository_class(Repository)
        upload_app = repository.upload_app

        # When
        filename, result = self._upload_app(force=True)

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        upload_app.assert_called_once_with(filename, overwrite=True)
        self.assertEqual(result.exit_code, 0)


class TestAppsMetadataMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.app_name = 'mayavi'
        self.app_version = '2.2'
        self.app_build = '1'
        self.app_full_version = '{0}-{1}'.format(
            self.app_version, self.app_build)
        self.python_tag = 'cp27'
        self.initial_args = ['--url', 'brood-dev.invalid', 'apps', 'metadata']
        self.final_args = [
            self.organization, self.repository, self.platform, self.python_tag,
            self.app_name, self.app_full_version]

    def _upload_app(self):
        with self.runner.isolated_filesystem() as tempdir:
            filename = os.path.join(tempdir, 'mayavi.app')
            with open(filename, 'w') as fh:
                fh.write('data')

            result = self.runner.invoke(
                main.hatcher,
                args=self.initial_args + self.final_args + [filename],
            )

        return filename, result

    @patch_repository
    def test_app_metadata(self, Repository):
        # Given
        expected = {'id': 'mayavi',
                    'name': 'Mayavi',
                    'version': '2.2',
                    'build': 1,
                    'python_tag': 'cp27'}
        repository, platform_repo = self._mock_repository_class(Repository)
        app_metadata = platform_repo.app_metadata
        app_metadata.return_value = expected

        # When
        result = self.runner.invoke(
            main.hatcher,
            args=self.initial_args + self.final_args,
        )

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        repository.platform.assert_called_once_with(self.platform)
        app_metadata.assert_called_once_with(
            self.python_tag, self.app_name, self.app_full_version)
        self.assertEqual(json.loads(result.output), expected)
        self.assertEqual(result.exit_code, 0)


class TestListAppsMain(MainTestingMixin, unittest.TestCase):

    def setUp(self):
        MainTestingMixin.setUp(self)
        self.host = 'http://brood-dev'
        self.app_name = 'mayavi'
        self.app_version = '2.2'
        self.app_build = '1'
        self.initial_args = ['--url', self.host, 'apps', 'list']
        self.final_args = [
            self.organization, self.repository, self.platform]

    @responses.activate
    def test_list_apps(self):
        # Given
        given_index = {
            'cp27': {
                'numpy.demo': {
                    '1.0': {
                        '1': {
                            'name': 'Numpy demo',
                            'description': 'Simple numpy demo',
                            'python_tag': 'cp27',
                        },
                    },
                },
                'mayavi.demo': {
                    '4.6.0': {
                        '1': {
                            'name': 'Mayavi demo',
                            'description': 'Simple mayavi demo',
                            'python_tag': 'cp27',
                        },
                    },
                },
            },
            'py2': {
                'purepython': {
                    '1.0.0': {
                        '2': {
                            'name': 'Pure Python',
                            'description': 'None',
                            'python_tag': 'py2',
                        },
                    },
                },
            },
        }
        expected = textwrap.dedent("""\
        App Name     Version    Python Tag
        -----------  ---------  ------------
        mayavi.demo  4.6.0-1    cp27
        numpy.demo   1.0-1      cp27
        purepython   1.0.0-2    py2
        """)

        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=self.host,
                uri=URLS.indices.apps.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                )
            ),
            body=json.dumps(given_index),
            status=200,
            content_type='application/json'
        )

        # When
        result = self.runner.invoke(
            main.hatcher,
            args=self.initial_args + self.final_args,
        )

        # Then
        self.assertEqual(result.output, expected)
        self.assertEqual(result.exit_code, 0)


class TestListEggsMain(MainTestingMixin, unittest.TestCase):

    @patch_repository
    def test_list_eggs(self, Repository):
        # Given
        python_tag = 'cp27'
        egg_names = [
            {'name': 'nose-1.3.0-1.egg', 'python_tag': 'py2'},
            {'name': 'MKL-10.3-3.egg', 'python_tag': 'none'},
            {'name': 'numpy-1.8.0-1.egg', 'python_tag': 'cp27'},
        ]
        sorted_metadata = sorted((item['name'], item['python_tag'])
                                 for item in egg_names)
        headers = ['Egg Name', 'Python Tag']
        expected = tabulate(sorted_metadata, headers=headers) + '\n'

        repository, platform_repo = self._mock_repository_class(Repository)
        list_eggs = platform_repo.list_eggs
        list_eggs.return_value = egg_names

        args = ['--url', 'brood-dev.invalid', 'eggs', 'list',
                self.organization, self.repository, self.platform, python_tag]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.output, expected)
        self.assertEqual(result.exit_code, 0)
        self.assertRepositoryConstructedCorrectly(Repository)
        list_eggs.assert_called_once_with(python_tag)


class TestListRuntimesMain(MainTestingMixin, unittest.TestCase):

    @patch_repository
    def test_list_apps(self, Repository):
        # Given
        runtimes = ['runtime2', 'runtime1']
        expected = '{0}\n'.format('\n'.join(sorted(runtimes)))

        repository, platform_repo = self._mock_repository_class(Repository)
        list_runtimes = platform_repo.list_runtimes
        list_runtimes.return_value = runtimes

        args = ['--url', 'brood-dev.invalid', 'runtimes', 'list',
                self.organization, self.repository, self.platform]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        list_runtimes.assert_called_once_with()
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)


class TestMainOrganizationActions(MainTestingMixin, unittest.TestCase):

    @patch_brood_client
    def test_create_organization(self, BroodClient):
        # Given
        description = 'Acme Co.'
        brood_client = self._mock_brood_client_class(BroodClient)
        create_organization = brood_client.create_organization

        args = ['--url', 'brood-dev.invalid', 'organizations', 'create',
                self.organization, description]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        create_organization.assert_called_once_with(
            self.organization, description)
        self.assertEqual(result.exit_code, 0)

    @patch_brood_client
    def test_list_organizations(self, BroodClient):
        # Given
        brood_client = self._mock_brood_client_class(BroodClient)
        list_organizations = brood_client.list_organizations
        list_organizations.return_value = ['one', 'two']
        expected_output = 'one\ntwo\n'

        args = ['--url', 'brood-dev.invalid', 'organizations', 'list']

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        list_organizations.assert_called_once_with()
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected_output)

    @patch_organization
    def test_create_repository(self, Organization):
        # Given
        description = 'a repository'
        organization = self._mock_organization_class(Organization)
        create_repository = organization.create_repository

        args = ['--url', 'brood-dev.invalid', 'repositories', 'create',
                self.organization, self.repository, description]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertOrganizationConstructedCorrectly(Organization)
        create_repository.assert_called_once_with(self.repository, description)
        self.assertEqual(result.exit_code, 0)

    @patch_repository
    def test_delete_repository(self, Repository):
        # Given
        repository, platform_repo = self._mock_repository_class(Repository)
        delete = repository.delete

        args = ['--url', 'brood-dev.invalid', 'repositories', 'delete',
                self.organization, self.repository]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        delete.assert_called_once_with(force=False)
        self.assertEqual(result.exit_code, 0)

    @patch_repository
    def test_delete_repository_force(self, Repository):
        # Given
        repository, platform_repo = self._mock_repository_class(Repository)
        delete = repository.delete

        args = ['--url', 'brood-dev.invalid', 'repositories', 'delete',
                '--force', self.organization, self.repository]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertRepositoryConstructedCorrectly(Repository)
        delete.assert_called_once_with(force=True)
        self.assertEqual(result.exit_code, 0)

    @patch_organization
    def test_list_repositories(self, Organization):
        # Given
        repositories = ['dev', 'staging', 'prod']
        expected = '{0}\n'.format('\n'.join(sorted(repositories)))
        organization = self._mock_organization_class(Organization)
        list_repositories = organization.list_repositories
        list_repositories.return_value = repositories

        args = ['--url', 'brood-dev.invalid', 'repositories', 'list',
                self.organization]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertOrganizationConstructedCorrectly(Organization)
        list_repositories.assert_called_once_with()
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)

    @patch_organization
    def test_list_teams(self, Organization):
        # Given
        teams = [{'name': 'dev-team'}, {'name': 'prod-team'}]
        expected = '{0}\n'.format(
            '\n'.join(sorted(team['name'] for team in teams)))
        organization = self._mock_organization_class(Organization)
        list_teams = organization.list_teams
        list_teams.return_value = teams

        args = ['--url', 'brood-dev.invalid', 'teams', 'list',
                self.organization]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertOrganizationConstructedCorrectly(Organization)
        list_teams.assert_called_once_with()
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)

    @patch_organization
    def test_create_team(self, Organization):
        # Given
        team_name = 'new-team'
        group_name = 'some-group'
        organization = self._mock_organization_class(Organization)
        create_team = organization.create_team

        args = ['--url', 'brood-dev.invalid', 'teams', 'create',
                self.organization, team_name, group_name]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertOrganizationConstructedCorrectly(Organization)
        create_team.assert_called_once_with(team_name, group_name)
        self.assertEqual(result.exit_code, 0)

    @patch_team
    def test_delete_team(self, Team):
        # Given
        team = self._mock_team_class(Team)
        delete_team = team.delete

        args = ['--url', 'brood-dev.invalid', 'teams', 'delete',
                self.organization, self.team]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertTeamConstructedCorrectly(Team)
        delete_team.assert_called_once_with()
        self.assertEqual(result.exit_code, 0)

    @patch_organization
    def test_create_user(self, Organization):
        # Given
        organization = self._mock_organization_class(Organization)
        create_user = organization.create_user

        args = ['--url', 'brood-dev.invalid', 'users', 'create',
                self.organization, self.user]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertOrganizationConstructedCorrectly(Organization)
        create_user.assert_called_once_with(self.user)
        self.assertEqual(result.exit_code, 0)

    @patch_user
    def test_delete_user(self, User):
        # Given
        user = self._mock_user_class(User)
        delete_user = user.delete

        args = ['--url', 'brood-dev.invalid', 'users', 'delete',
                self.organization, self.user]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertUserConstructedCorrectly(User)
        delete_user.assert_called_once_with()
        self.assertEqual(result.exit_code, 0)


class TestMainTeamActions(MainTestingMixin, unittest.TestCase):

    @patch_team
    def test_team_metadata(self, Team):
        # Given
        metadata = {'name': 'team'}
        expected = '{}\n'.format(metadata)
        team = self._mock_team_class(Team)
        get_metadata = team.metadata
        get_metadata.return_value = metadata

        args = ['--url', 'brood-dev.invalid', 'teams', 'metadata',
                self.organization, self.team]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        get_metadata.assert_called_once_with()
        self.assertEqual(result.output, expected)

    @patch_team
    def test_list_repositories(self, Team):
        # Given
        repositories = ["repository1", "repository2"]
        expected = '{0}\n'.format('\n'.join(sorted(repositories)))
        team = self._mock_team_class(Team)
        list_repositories = team.list_repositories
        list_repositories.return_value = repositories

        args = ['--url', 'brood-dev.invalid', 'teams', 'repositories', 'list',
                self.organization, self.team]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        list_repositories.assert_called_once_with()
        self.assertEqual(result.output, expected)

    @patch_repository
    @patch_team
    def test_add_repository_to_team(self, Team, Repository):
        # Given
        team = self._mock_team_class(Team)
        repository, _ = self._mock_repository_class(Repository)
        add_repository = team.add_repository

        args = ['--url', 'brood-dev.invalid', 'teams', 'repositories', 'add',
                self.organization, self.team, self.repository]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        add_repository.assert_called_once_with(repository)

    @patch_repository
    @patch_team
    def test_remove_repository_from_team(self, Team, Repository):
        # Given
        team = self._mock_team_class(Team)
        repository, _ = self._mock_repository_class(Repository)
        remove_repository = team.remove_repository

        args = ['--url', 'brood-dev.invalid', 'teams', 'repositories',
                'remove', self.organization, self.team, self.repository]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        remove_repository.assert_called_once_with(repository)

    @patch_repository
    @patch_team
    def test_query_team_repository_true(self, Team, Repository):
        # Given
        team = self._mock_team_class(Team)
        repository, _ = self._mock_repository_class(Repository)
        query_repository_access = team.query_repository_access
        query_repository_access.return_value = True

        args = ['--url', 'brood-dev.invalid', 'teams', 'repositories', 'query',
                self.organization, self.team, self.repository]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        query_repository_access.assert_called_once_with(repository)
        self.assertRegexpMatches(
            result.output, r'has access to')

    @patch_repository
    @patch_team
    def test_query_team_repository_false(self, Team, Repository):
        # Given
        team = self._mock_team_class(Team)
        repository, _ = self._mock_repository_class(Repository)
        query_repository_access = team.query_repository_access
        query_repository_access.return_value = False

        args = ['--url', 'brood-dev.invalid', 'teams', 'repositories', 'query',
                self.organization, self.team, self.repository]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 1)
        query_repository_access.assert_called_once_with(repository)
        self.assertRegexpMatches(
            result.output, r'does not have access to')

    @patch_team
    def test_list_users(self, Team):
        # Given
        users = ["user1", "user2"]
        expected = '{0}\n'.format('\n'.join(sorted(users)))
        team = self._mock_team_class(Team)
        list_users = team.list_users
        list_users.return_value = users

        args = ['--url', 'brood-dev.invalid', 'teams', 'members', 'list',
                self.organization, self.team]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        list_users.assert_called_once_with()
        self.assertEqual(result.output, expected)

    @patch_user
    @patch_team
    def test_add_user_to_team(self, Team, User):
        # Given
        team = self._mock_team_class(Team)
        user = self._mock_user_class(User)
        add_user = team.add_user

        args = ['--url', 'brood-dev.invalid', 'teams', 'members', 'add',
                self.organization, self.team, self.user]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        add_user.assert_called_once_with(user)

    @patch_user
    @patch_team
    def test_remove_user_from_team(self, Team, User):
        # Given
        team = self._mock_team_class(Team)
        user = self._mock_user_class(User)
        remove_user = team.remove_user

        args = ['--url', 'brood-dev.invalid', 'teams', 'members', 'remove',
                self.organization, self.team, self.user]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        remove_user.assert_called_once_with(user)

    @patch_user
    @patch_team
    def test_query_team_member_true(self, Team, User):
        # Given
        team = self._mock_team_class(Team)
        user = self._mock_user_class(User)
        query_user_access = team.query_user_access
        query_user_access.return_value = True

        args = ['--url', 'brood-dev.invalid', 'teams', 'members', 'query',
                self.organization, self.team, self.user]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        query_user_access.assert_called_once_with(user)
        self.assertRegexpMatches(
            result.output, r'has access to')

    @patch_user
    @patch_team
    def test_query_team_member_false(self, Team, User):
        # Given
        team = self._mock_team_class(Team)
        user = self._mock_user_class(User)
        query_user_access = team.query_user_access
        query_user_access.return_value = False

        args = ['--url', 'brood-dev.invalid', 'teams', 'members', 'query',
                self.organization, self.team, self.user]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 1)
        query_user_access.assert_called_once_with(user)
        self.assertRegexpMatches(
            result.output, r'does not have access to')


class TestHttpErrors(MainTestingMixin, unittest.TestCase):

    @responses.activate
    def test_http_error_debug_flag(self):
        # Given
        python_tag = 'pp27'
        host = 'http://brood-dev'
        error = 'Authentication failed'
        body = {'error': error}
        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.indices.eggs.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                    python_tag=python_tag,
                ),
            ),
            status=401,
            body=json.dumps(body),
            content_type='application/json'
        )

        # When
        args = ['--debug', '-u', host, 'eggs', 'list', self.organization,
                self.repository, self.platform, python_tag]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertIsInstance(result.exception, HTTPError)
        self.assertEqual(result.exit_code, -1)

    @responses.activate
    def test_json_formatted_error_on_download(self):
        # Given
        python_tag = 'pp27'
        host = 'http://brood-dev'
        error = 'Authentication failed'
        body = {'error': error}
        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.indices.eggs.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                    python_tag=python_tag,
                ),
            ),
            status=401,
            body=json.dumps(body),
            content_type='application/json'
        )

        # When
        args = ['-u', host, 'eggs', 'list', self.organization, self.repository,
                self.platform, python_tag]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertIsInstance(result.exception, SystemExit)
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(result.output.strip(), error)

    @responses.activate
    def test_bad_json_formatted_error_on_download(self):
        # Given
        python_tag = 'cp27'
        host = 'http://brood-dev'
        error = 'Authentication failed'
        body = {'key': error}
        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.indices.eggs.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                    python_tag=python_tag,
                ),
            ),
            status=401,
            body=json.dumps(body),
            content_type='application/json'
        )

        # When
        args = ['-u', host, 'eggs', 'list', self.organization, self.repository,
                self.platform, python_tag]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertIsInstance(result.exception, HTTPError)
        self.assertEqual(abs(result.exit_code), 1)

    @responses.activate
    def test_non_json_error_on_download(self):
        # Given
        host = 'http://brood-dev'
        error = 'Some error'
        python_tag = 'ip27'
        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.indices.eggs.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                    python_tag=python_tag,
                ),
            ),
            status=404,
            body=error,
            content_type='text/plain'
        )

        # When/Then
        args = ['-u', host, 'eggs', 'list', self.organization, self.repository,
                self.platform, python_tag]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertIsInstance(result.exception, HTTPError)
        self.assertEqual(abs(result.exit_code), 1)

    @responses.activate
    def test_non_json_authentication_error_on_upload(self):
        # Given
        host = 'http://brood-dev'
        error = 'Some error'
        responses.add(
            responses.POST,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.data.eggs.upload.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                ),
            ),
            status=401,
            body=error,
            content_type='text/plain'
        )

        # When/Then
        args = ['-u', host, 'eggs', 'upload', self.organization,
                self.repository, self.platform, __file__]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertIsInstance(result.exception, SystemExit)
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(result.output.strip(), 'Authentication failed')

    @responses.activate
    def test_debug_flag_on_upload(self):
        # Given
        host = 'http://brood-dev'
        error = 'Some error'
        responses.add(
            responses.POST,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.data.eggs.upload.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                ),
            ),
            status=401,
            body=error,
            content_type='text/plain'
        )

        # When/Then
        args = ['--debug', '-u', host, 'eggs', 'upload', self.organization,
                self.repository, self.platform, __file__]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertIsInstance(result.exception, HTTPError)
        self.assertEqual(result.exit_code, -1)

    @responses.activate
    def test_non_json_not_found_error_on_upload(self):
        # Given
        host = 'http://brood-dev'
        error = 'Some error'
        responses.add(
            responses.POST,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.data.eggs.upload.format(
                    organization_name=self.organization,
                    repository_name=self.repository,
                    platform=self.platform,
                ),
            ),
            status=404,
            body=error,
            content_type='text/plain'
        )

        # When/Then
        args = ['-u', host, 'eggs', 'upload', self.organization,
                self.repository, self.platform, __file__]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        expected_error = "No such repository: '{}/{}'".format(
            self.organization, self.repository)
        self.assertIsInstance(result.exception, SystemExit)
        self.assertEqual(result.exit_code, -1)
        self.assertEqual(result.output.strip(), expected_error)


class TestApiTokensMain(MainTestingMixin, unittest.TestCase):

    @responses.activate
    def test_create_api_token(self):
        # Given
        host = 'http://brood-dev'

        token_name = 'my-token'
        token = 'some-token'
        return_value = {'name': token_name, 'token': token}

        expected = textwrap.dedent("""\
        New Token Name    New Token
        ----------------  -----------
        {: <16}  {}
        """.format(token_name, token))

        responses.add(
            responses.POST,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.tokens.api.format(),
            ),
            status=200,
            body=json.dumps(return_value),
            content_type='application/json',
        )

        # When
        args = ['-u', host, 'api-tokens', 'create', token_name]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertEqual(result.output, expected)

    @responses.activate
    def test_delete_api_token(self):
        # Given
        host = 'http://brood-dev'

        token_name = 'my-token'

        responses.add(
            responses.DELETE,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.tokens.api.delete.format(name=token_name),
            ),
            status=204,
        )

        # When
        args = ['-u', host, 'api-tokens', 'delete', token_name]
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, '')
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_list_api_tokens(self):
        # Given
        host = 'http://brood-dev'
        tokens = [
            {
                'name': 'token1',
                'created': datetime(2014, 1, 1, 1, 2, 2, 2).isoformat(),
                'last_used': datetime(2014, 2, 3, 4, 5, 6, 7).isoformat(),
            },
            {
                'name': 'token3',
                'created': datetime(2013, 3, 3, 3, 4, 4, 4).isoformat(),
                'last_used': None,
            },
            {
                'name': 'token2',
                'created': datetime(2013, 2, 2, 2, 3, 3, 3).isoformat(),
                'last_used': datetime(2014, 7, 6, 5, 4, 3, 2).isoformat(),
            },
        ]

        expected = textwrap.dedent("""\
        Name    Created                     Last Used
        ------  --------------------------  --------------------------
        token1  2014-01-01T01:02:02.000002  2014-02-03T04:05:06.000007
        token2  2013-02-02T02:03:03.000003  2014-07-06T05:04:03.000002
        token3  2013-03-03T03:04:04.000004
        """)

        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.tokens.api.format(),
            ),
            status=200,
            body=json.dumps({'tokens': tokens}),
            content_type='application/json',
        )

        # When
        args = ['-u', host, 'api-tokens', 'list']
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertEqual(result.output, expected)


class TestServerActionsMain(MainTestingMixin, unittest.TestCase):

    @responses.activate
    def test_list_platforms(self):
        # Given
        host = 'http://brood-dev'
        platforms = [
            'osx-x86',
            'osx-x86_64',
            'rh5-x86',
            'rh5-x86_64',
        ]
        expected = textwrap.dedent("""\
        Platforms
        -----------
        {}
        """).format('\n'.join(sorted(platforms)))
        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.metadata.platforms.format(),
            ),
            status=200,
            body=json.dumps({'platforms': platforms}),
            content_type='application/json',
        )

        # When
        args = ['-u', host, 'platforms', 'list']
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertEqual(result.output, expected)

    @responses.activate
    def test_list_top_level_python_tags(self):
        # Given
        host = 'http://brood-dev'
        python_tags = [
            'cp27',
            'pp27',
            'cp34'
        ]
        expected = textwrap.dedent("""\
        Python Tag
        ------------
        {}
        """).format('\n'.join(sorted(python_tags)))

        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.metadata.python_tags.format(),
            ),
            status=200,
            body=json.dumps({'python_tags': python_tags}),
            content_type='application/json',
        )

        # When
        args = ['-u', host, 'python-tags', 'list']
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertEqual(result.output, expected)

    @responses.activate
    def test_list_all_python_tags(self):
        # Given
        host = 'http://brood-dev'
        python_tags = [
            'cp27',
            'pp27',
            'cp34',
            'py2',
            'ip2',
        ]
        expected = textwrap.dedent("""\
        Python Tag
        ------------
        {}
        """).format('\n'.join(sorted(python_tags)))

        responses.add(
            responses.GET,
            '{host}{uri}'.format(
                host=host,
                uri=URLS.metadata.python_tags.all.format(),
            ),
            status=200,
            body=json.dumps({'python_tags': python_tags}),
            content_type='application/json',
        )

        # When
        args = ['-u', host, 'python-tags', 'list', '--all']
        result = self.runner.invoke(main.hatcher, args)

        # Then
        self.assertEqual(result.output, expected)
