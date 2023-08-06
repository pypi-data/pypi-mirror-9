import json

import requests
import responses

from hatcher.testing import unittest
from ..brood_url_handler import BroodURLHandler
from ..repository import Repository
from ..team import Team
from ..url_templates import URLS
from ..user import User


class TestTeam(unittest.TestCase):

    def setUp(self):
        self.url_handler = BroodURLHandler('http://brood-dev')
        self.team = Team('enthought', 'team', self.url_handler)

    @responses.activate
    def test_delete_team(self):
        # Given
        responses.add(
            responses.DELETE,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.format(
                    organization_name='enthought',
                    team_name='team',
                ),
            ),
        )

        # When
        self.team.delete()

        # Then
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_get_metadata(self):
        # Given
        expected = {}
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.format(
                    organization_name='enthought',
                    team_name='team',
                ),
            ),
            body=json.dumps(expected),
            status=200,
            content_type='application/json',
        )

        # When
        metadata = self.team.metadata()

        # Then
        self.assertEqual(metadata, expected)

    @responses.activate
    def test_list_repositories(self):
        # Given
        expected = ['free', 'commercial']
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.repositories.format(
                    organization_name='enthought',
                    team_name='team',
                ),
            ),
            body=json.dumps({'repositories': expected}),
            content_type='application/json',
        )

        # When
        repositories = self.team.list_repositories()

        # Then
        self.assertEqual(repositories, expected)

    @responses.activate
    def test_add_repository(self):
        # Given
        repository = Repository(
            'enthought', 'free', url_handler=self.url_handler)
        responses.add(
            responses.PUT,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.repositories.query.format(
                    organization_name='enthought',
                    team_name='team',
                    repository_name='free',
                ),
            ),
            status=204,
        )

        # When
        self.team.add_repository(repository)

        # Then
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_remove_repository(self):
        # Given
        repository = Repository(
            'enthought', 'free', url_handler=self.url_handler)
        responses.add(
            responses.DELETE,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.repositories.query.format(
                    organization_name='enthought',
                    team_name='team',
                    repository_name='free',
                ),
            ),
            status=204,
        )

        # When
        self.team.remove_repository(repository)

        # Then
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_query_repository_access_true(self):
        # Given
        repository = Repository(
            'enthought', 'free', url_handler=self.url_handler)
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.repositories.query.format(
                    organization_name='enthought',
                    team_name='team',
                    repository_name='free',
                ),
            ),
            status=204,
        )

        # When
        access = self.team.query_repository_access(repository)

        # Then
        self.assertTrue(access)

    @responses.activate
    def test_query_repository_access_false(self):
        # Given
        repository = Repository(
            'enthought', 'free', url_handler=self.url_handler)
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.repositories.query.format(
                    organization_name='enthought',
                    team_name='team',
                    repository_name='free',
                ),
            ),
            status=404,
        )

        # When
        access = self.team.query_repository_access(repository)

        # Then
        self.assertFalse(access)

    @responses.activate
    def test_query_repository_access_error(self):
        # Given
        repository = Repository(
            'enthought', 'free', url_handler=self.url_handler)
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.repositories.query.format(
                    organization_name='enthought',
                    team_name='team',
                    repository_name='free',
                ),
            ),
            status=403,
        )

        # When/Then
        with self.assertRaises(requests.exceptions.HTTPError):
            self.team.query_repository_access(repository)

    @responses.activate
    def test_list_users(self):
        # Given
        expected = ['user1@acme.org', 'user2@acme.org']
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.members.format(
                    organization_name='enthought',
                    team_name='team',
                ),
            ),
            body=json.dumps({'members': expected}),
            content_type='application/json',
        )

        # When
        members = self.team.list_users()

        # Then
        self.assertEqual(members, expected)

    @responses.activate
    def test_add_user(self):
        # Given
        user = User('acme', 'user@acme.org', url_handler=self.url_handler)
        responses.add(
            responses.PUT,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.members.query.format(
                    organization_name='enthought',
                    team_name='team',
                    email=user.email,
                ),
            ),
            status=204,
        )

        # When
        self.team.add_user(user)

        # Then
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_remove_user(self):
        # Given
        user = User('acme', 'user@acme.org', url_handler=self.url_handler)
        responses.add(
            responses.DELETE,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.members.query.format(
                    organization_name='enthought',
                    team_name='team',
                    email=user.email,
                ),
            ),
            status=204,
        )

        # When
        self.team.remove_user(user)

        # Then
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_query_user_access_true(self):
        # Given
        user = User('acme', 'user@acme.org', url_handler=self.url_handler)
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.members.query.format(
                    organization_name='enthought',
                    team_name='team',
                    email=user.email,
                ),
            ),
            status=204,
        )

        # When
        access = self.team.query_user_access(user)

        # Then
        self.assertTrue(access)

    @responses.activate
    def test_query_user_access_false(self):
        # Given
        user = User('acme', 'user@acme.org', url_handler=self.url_handler)
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.members.query.format(
                    organization_name='enthought',
                    team_name='team',
                    email=user.email,
                ),
            ),
            status=404,
        )

        # When
        access = self.team.query_user_access(user)

        # Then
        self.assertFalse(access)

    @responses.activate
    def test_query_user_access_error(self):
        # Given
        user = User('acme', 'user@acme.org', url_handler=self.url_handler)
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.teams.members.query.format(
                    organization_name='enthought',
                    team_name='team',
                    email=user.email,
                ),
            ),
            status=403,
        )

        # When/Then
        with self.assertRaises(requests.exceptions.HTTPError):
            self.team.query_user_access(user)
