from datetime import datetime
import json
import responses

from hatcher.testing import unittest
from ..brood_url_handler import BroodURLHandler
from ..brood_client import BroodClient
from ..organization import Organization
from ..url_templates import URLS
from .common import JsonSchemaTestMixin


class TestBroodClient(JsonSchemaTestMixin, unittest.TestCase):

    def setUp(self):
        self.url_handler = BroodURLHandler('http://brood-dev')
        self.brood = BroodClient(url_handler=self.url_handler)

    def test_get_organization(self):
        # When
        organization = self.brood.organization('acme')

        # Then
        self.assertIsInstance(organization, Organization)
        self.assertEqual(organization.name, 'acme')

    @responses.activate
    def test_create_organization(self):
        # Given
        expected = {
            'name': 'acme',
            'description': 'Acme co.',
        }
        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.organizations.format(),
            ),
        )

        # When
        self.brood.create_organization('acme', 'Acme co.')

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        self.assertHatcherUserAgent(request)
        self.assertJsonValid(request.body, 'create_organization.json')
        self.assertEqual(json.loads(request.body), expected)
        self.assertEqual(
            request.headers.get('Content-Type'), 'application/json')

    @responses.activate
    def test_list_organizations(self):
        # Given
        expected = ['enthought', 'acme']
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.organizations.format(),
            ),
            body=json.dumps({'organizations': expected}),
        )

        # When
        organizations = self.brood.list_organizations()

        # Then
        call, = responses.calls
        request, response = call
        self.assertHatcherUserAgent(request)
        self.assertEqual(organizations, list(sorted(expected)))

    @responses.activate
    def test_create_api_token(self):
        # Given
        name = 'my-token'
        expected = {'name': name, 'token': 1234}
        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.tokens.api.format(),
            ),
            status=200,
            body=json.dumps(expected),
            content_type='application/json',
        )

        # When
        created_token = self.brood.create_api_token(name)

        # Then
        self.assertEqual(created_token, expected)

    @responses.activate
    def test_delete_api_token(self):
        # Given
        name = 'my-token'
        responses.add(
            responses.DELETE,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.tokens.api.delete.format(name=name),
            ),
            status=204,
        )

        # When
        self.brood.delete_api_token(name)

        # Then
        self.assertEqual(len(responses.calls), 1)

    @responses.activate
    def test_list_api_tokens(self):
        # Given
        expected = [
            {
                'name': 'token1',
                'created': datetime(2014, 1, 1, 1, 2, 2, 2).isoformat(),
                'last_used': datetime(2014, 2, 3, 4, 5, 6, 7).isoformat(),
            },
            {
                'name': 'token2',
                'created': datetime(2013, 2, 2, 2, 3, 3, 3).isoformat(),
                'last_used': datetime(2014, 7, 6, 5, 4, 3, 2).isoformat(),
            },
            {
                'name': 'token3',
                'created': datetime(2013, 3, 3, 3, 4, 4, 4).isoformat(),
                'last_used': None,
            },
        ]
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.tokens.api.format(),
            ),
            status=200,
            body=json.dumps({'tokens': expected}),
            content_type='application/json',
        )

        # When
        tokens = self.brood.list_api_tokens()

        # Then
        self.assertEqual(tokens, expected)

    @responses.activate
    def test_list_platforms(self):
        # Given
        expected = [
            'osx-x86',
            'osx-x86_64',
            'rh5-x86',
            'rh5-x86_64',
        ]
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.platforms.format(),
            ),
            status=200,
            body=json.dumps({'platforms': expected}),
            content_type='application/json',
        )

        # When
        platforms = self.brood.list_platforms()

        # Then
        self.assertEqual(platforms, expected)

    @responses.activate
    def test_list_python_tags(self):
        # Given
        expected = [
            'cp27',
            'pp27',
            'cp34',
        ]
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.python_tags.format(),
            ),
            status=200,
            body=json.dumps({'python_tags': expected}),
            content_type='application/json',
        )

        # When
        platforms = self.brood.list_python_tags()

        # Then
        self.assertEqual(set(platforms), set(expected))

    @responses.activate
    def test_list_all_python_tags(self):
        # Given
        expected = [
            'cp27',
            'pp27',
            'cp34',
            'py2',
        ]
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.python_tags.all.format(),
            ),
            status=200,
            body=json.dumps({'python_tags': expected}),
            content_type='application/json',
        )

        # When
        platforms = self.brood.list_python_tags(list_all=True)

        # Then
        self.assertEqual(set(platforms), set(expected))
