import cgi
import json

import jsonschema
from jsonschema.exceptions import ValidationError
from six import BytesIO

from brood_json_schemas import get_schema


class JsonSchemaTestMixin(object):

    def assertJsonValid(self, json_string, schema_name):
        schema = get_schema(schema_name)
        try:
            json_data = json.loads(json_string)
        except ValueError as e:
            self.fail('Unable to load json string: {0!r}'.format(e))

        try:
            jsonschema.validate(json_data, schema)
        except ValidationError as e:
            self.fail('JSON does not validate against schema: {0!r}'.format(e))

    def _parse_multipart_data(self, data, headers):
        body = BytesIO(data)
        _, pdict = cgi.parse_header(headers['Content-Type'])
        pdict['boundary'] = pdict['boundary'].encode('utf-8')
        multipart = cgi.parse_multipart(body, pdict)
        return next(iter(multipart['data'])).decode('utf-8')

    def assertHatcherUserAgent(self, request):
        user_agent = request.headers['User-Agent']
        self.assertTrue(
            user_agent.startswith('hatcher/'),
            msg="Expected user agent to start with 'hatcher/'")
