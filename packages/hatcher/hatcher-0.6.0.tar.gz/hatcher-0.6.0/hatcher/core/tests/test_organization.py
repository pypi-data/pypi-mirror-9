import json

import responses

from hatcher.testing import unittest
from ..brood_url_handler import BroodURLHandler
from ..organization import Organization
from ..repository import Repository
from ..team import Team
from ..url_templates import URLS
from ..user import User
from .common import JsonSchemaTestMixin


class TestOrganization(JsonSchemaTestMixin, unittest.TestCase):

    def setUp(self):
        self.url_handler = BroodURLHandler('http://brood-dev')
        self.organization = Organization(
            'acme', url_handler=self.url_handler)

    def test_get_repository(self):
        # When
        repository = self.organization.repository('free')

        # Then
        self.assertIsInstance(repository, Repository)
        self.assertEqual(repository.organization_name, self.organization.name)
        self.assertEqual(repository.name, 'free')

    @responses.activate
    def test_create_repository(self):
        # Given
        expected = {
            'name': 'dev',
            'description': 'Dev Repository',
        }
        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.organizations.repositories.format(
                    organization_name='acme',
                ),
            ),
        )

        # When
        repository = self.organization.create_repository(
            'dev', 'Dev Repository')

        # Then
        self.assertEqual(repository.organization_name, self.organization.name)
        self.assertEqual(repository.name, 'dev')
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        self.assertJsonValid(request.body, 'create_repository.json')
        self.assertEqual(json.loads(request.body), expected)
        self.assertEqual(
            request.headers.get('Content-Type'), 'application/json')

    def test_get_team(self):
        # When
        team = self.organization.team('free-read')

        # Then
        self.assertIsInstance(team, Team)
        self.assertEqual(team.organization_name, self.organization.name)
        self.assertEqual(team.name, 'free-read')

    @responses.activate
    def test_create_team(self):
        # Given
        group_name = 'read_repository'
        team_name = 'team'
        expected = {
            'name': team_name,
            'group': group_name,
        }
        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.organizations.teams.format(
                    organization_name='acme',
                ),
            ),
        )

        # When
        team = self.organization.create_team(team_name, group_name)

        # Then
        self.assertEqual(team.organization_name, self.organization.name)
        self.assertEqual(team.name, team_name)
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        self.assertJsonValid(request.body, 'create_organization_team.json')
        self.assertEqual(json.loads(request.body), expected)
        self.assertEqual(
            request.headers.get('Content-Type'), 'application/json')

    def test_get_user(self):
        # When
        user = self.organization.user('user@acme.org')

        # Then
        self.assertIsInstance(user, User)
        self.assertEqual(user.organization_name, self.organization.name)
        self.assertEqual(user.email, 'user@acme.org')

    @responses.activate
    def test_create_user(self):
        # Given
        email = 'user@acme.org'
        expected = {
            'email': email,
        }
        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.organizations.users.format(
                    organization_name='acme',
                ),
            ),
            status=201,
        )

        # When
        user = self.organization.create_user(email)

        # Then
        self.assertEqual(user.organization_name, self.organization.name)
        self.assertEqual(user.email, email)
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        self.assertJsonValid(request.body, 'create_organization_user.json')
        self.assertEqual(json.loads(request.body), expected)
        self.assertEqual(
            request.headers.get('Content-Type'), 'application/json')

    @responses.activate
    def test_create_user_with_teams(self):
        # Given
        email = 'user@acme.org'
        expected = {
            'email': email,
            'teams': ['dev', 'prod'],
        }
        teams = [
            Team('acme', 'dev', url_handler=self.url_handler),
            Team('acme', 'prod', url_handler=self.url_handler),
        ]
        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.organizations.users.format(
                    organization_name='acme',
                ),
            ),
            status=201,
        )

        # When
        user = self.organization.create_user(email, teams)

        # Then
        self.assertEqual(user.organization_name, self.organization.name)
        self.assertEqual(user.email, email)
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        self.assertEqual(json.loads(request.body), expected)

    @unittest.expectedFailure
    def test_delete_organization(self):
        # When
        self.organization.delete()

        # Then
        self.assertEqual(len(responses.calls), 1)

    @unittest.expectedFailure
    def test_get_metadata(self):
        # When
        self.organization.metadata()

        # Then
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_list_repositories(self):
        # Given
        expected = ['free', 'commercial', 'testing']
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.organizations.repositories.format(
                    organization_name='acme',
                ),
            ),
            body=json.dumps({'repositories': expected}),
            content_type='application/json',
        )

        # When
        repositories = self.organization.list_repositories()

        # Then
        self.assertEqual(repositories, expected)

    @responses.activate
    def test_list_teams(self):
        # Given
        expected = ['free-read', 'commercial-read', 'index']
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.organizations.teams.format(
                    organization_name='acme',
                ),
            ),
            body=json.dumps({'teams': expected}),
            content_type='application/json',
        )

        # When
        repositories = self.organization.list_teams()

        # Then
        self.assertEqual(repositories, expected)

    @unittest.expectedFailure
    @responses.activate
    def test_list_users(self):
        # Given
        expected = ['user@acme.org', 'admin@acme.org']
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.organizations.users.format(
                    organization_name='acme',
                ),
            ),
            body=json.dumps({'users': expected})
        )

        # When
        users = self.organization.list_users()

        # Then
        self.assertEqual(users, expected)
