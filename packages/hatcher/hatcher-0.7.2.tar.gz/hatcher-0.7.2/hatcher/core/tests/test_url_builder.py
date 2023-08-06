import unittest

from ..url_templates import UrlBuilder


URLS = UrlBuilder(
    'root', '/api/v0/json',
    UrlBuilder(
        'admin', '/admin',
        UrlBuilder(
            'organizations', '/organizations',
            UrlBuilder('repositories', '/{organization_name}/repositories'),
            UrlBuilder('teams', '/{organization_name}/teams'),
            UrlBuilder('users', '/{organization_name}/users'),
        ),
    ),
    UrlBuilder('data', '/data'),
)


class TestUrlTemplates(unittest.TestCase):

    def test_root(self):
        self.assertEqual(URLS.format(), '/api/v0/json')

    def test_attribute_error(self):
        with self.assertRaises(AttributeError):
            URLS.no_attr

    def test_simple_tree(self):
        self.assertEqual(URLS.admin.format(), '/api/v0/json/admin')
        self.assertEqual(URLS.admin.organizations.format(),
                         '/api/v0/json/admin/organizations')

    def test_iter(self):
        urls = list(URLS)
        expected = [
            '/api/v0/json',
            '/api/v0/json/admin',
            '/api/v0/json/admin/organizations',
            '/api/v0/json/admin/organizations/{organization_name}/repositories',  # noqa
            '/api/v0/json/admin/organizations/{organization_name}/teams',
            '/api/v0/json/admin/organizations/{organization_name}/users',
            '/api/v0/json/data',
        ]
        self.assertEqual(urls, expected)
