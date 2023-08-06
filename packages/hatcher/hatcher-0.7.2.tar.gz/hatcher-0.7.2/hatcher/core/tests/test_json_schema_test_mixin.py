from hatcher.testing import unittest
from .common import JsonSchemaTestMixin


class TestJsonSchemaTestMixin(JsonSchemaTestMixin, unittest.TestCase):

    def test_fail_on_json_loading(self):
        with self.assertRaises(AssertionError):
            self.assertJsonValid('invalid-JSON', 'create_organization.json')

    def test_fail_on_invalid_json(self):
        with self.assertRaises(AssertionError):
            self.assertJsonValid('{}', 'create_organization.json')

    def test_success(self):
        json_string = '{"name": "acme", "description": "acme co"}'
        self.assertJsonValid(json_string, 'create_organization.json')
