import responses

from hatcher.testing import unittest
from ..auth import BroodBearerTokenAuth
from ..brood_url_handler import BroodURLHandler


class TestBroodClient(unittest.TestCase):

    @responses.activate
    def test_bearer_token_auth(self):
        # Given
        token = 'token'
        url_handler = BroodURLHandler(
            'http://brood-dev',
            auth=BroodBearerTokenAuth(token),
        )
        self.auth_header = None

        def callback(request):
            self.auth_header = request.headers.get('Authorization')
            return (200, {}, '')

        responses.add_callback(
            responses.GET,
            '{scheme}://{host}/'.format(
                scheme=url_handler.scheme,
                host=url_handler.host,
            ),
            callback,
        )

        # When
        url_handler.get('/')

        # Then
        self.assertEqual(len(responses.calls), 1)
        self.assertEqual(self.auth_header, 'Bearer {}'.format(token))
