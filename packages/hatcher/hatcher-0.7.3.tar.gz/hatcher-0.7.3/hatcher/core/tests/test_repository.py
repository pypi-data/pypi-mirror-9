import hashlib
import json
import os
import re
import shutil
import tempfile

import responses
import six

from hatcher.errors import ChecksumMismatchError
from hatcher.testing import make_testing_egg, unittest
from ..brood_url_handler import BroodURLHandler
from ..repository import Repository
from ..url_templates import URLS
from .common import JsonSchemaTestMixin


BODY_FILENAME_RE = re.compile(
    r'Content-Disposition: form-data; name="file"; filename="(.*?)"')


class TestRepository(JsonSchemaTestMixin, unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix='hatcher-', suffix='-tmp')
        self.temp_dir2 = tempfile.mkdtemp(prefix='hatcher-', suffix='-tmp')
        self.url_handler = BroodURLHandler('http://brood-dev')
        self.repository = Repository('enthought', 'free', self.url_handler)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    @responses.activate
    def test_delete_repository(self):
        # Given
        responses.add(
            responses.DELETE,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.repositories.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name
                ),
            ),
        )

        # When
        self.repository.delete()

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        self.assertRegexpMatches(request.url, r'^.*?\?force=False$')

    @responses.activate
    def test_delete_repository_force(self):
        # Given
        responses.add(
            responses.DELETE,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.repositories.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                ),
            ),
        )

        # When
        self.repository.delete(force=True)

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        self.assertRegexpMatches(request.url, r'^.*?\?force=True$')

    @unittest.expectedFailure
    def test_get_metadata(self):
        # Given
        expected = {}
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.repositories.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                ),
            ),
            body=json.dumps(expected),
            status=200,
            content_type='application/json',
        )

        # When
        metadata = self.repository.metadata()

        # Then
        self.assertEqual(metadata, expected)

    @unittest.expectedFailure
    def test_list_platforms(self):
        # Given
        expected = ['rh5-64', 'win-32', 'dos-16']
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}/platforms'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.admin.repositories.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                ),
            ),
            body=json.dumps({'platforms': expected}),
            status=200,
            content_type='application/json',
        )

        # When
        platform_names = self.repository.list_platforms()

        # Then
        self.assertEqual(platform_names, expected)

    def test_get_specific_platform(self):
        # Given
        platform_name = 'rh5-64'

        # When
        platform = self.repository.platform(platform_name)

        # Then
        self.assertEqual(platform.name, platform_name)

    @responses.activate
    def test_list_eggs(self):
        # Given
        python_tag = 'cp27'
        expected = [
            ('nose-1.3.0-1.egg', 'cp27'),
            ('numpy-1.8.0-1.egg', 'py2'),
        ]
        platform_name = 'rh5-64'
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.indices.eggs.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                    python_tag=python_tag,
                ),
            ),
            body=json.dumps({egg: {'python_tag': tag}
                             for egg, tag in expected}),
            status=200,
            content_type='application/json',
        )

        platform = self.repository.platform(platform_name)

        # When
        metadata = platform.list_eggs(python_tag)

        sorted_metadata = sorted((item['name'], item['python_tag'])
                                 for item in metadata)
        # Then
        self.assertEqual(
            list(sorted_metadata), list(sorted(expected)))

    @responses.activate
    def test_egg_index(self):
        # Given
        python_tag = 'cp34'
        expected = {
            "numpy-1.6.0-2.egg": {
                "size": 3382229,
                "md5": "41b0cfa9cff92d40b124c930f94332bd",
                "packages": [
                    "MKL 10.3-1"
                ],
                "type": "egg",
                "name": "numpy",
                "build": 2,
                "implementation_tag": "cp34",
                "available": True,
                "mtime": 1408370414.56413,
                "version": "1.6.0",
                "product": "free"
            },
        }
        platform_name = 'rh5-64'
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.indices.eggs.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                    python_tag=python_tag,
                ),
            ),
            body=json.dumps(expected),
            status=200,
            content_type='application/json',
        )

        platform = self.repository.platform(platform_name)

        # When
        metadata = platform.egg_index(python_tag)

        # Then
        self.assertEqual(metadata, expected)

    @responses.activate
    def test_get_egg_metadata(self):
        # Given
        python_tag = 'none'
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
        version = expected['version'] + '-1'
        platform_name = 'rh5-64'
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.artefacts.eggs.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                    python_tag=python_tag,
                    name='mkl',
                    version=version,
                )
            ),
            body=json.dumps(expected),
            status=200,
            content_type='application/json',
        )

        platform = self.repository.platform(platform_name)

        # When
        metadata = platform.egg_metadata(python_tag, 'mkl', version)

        # Then
        self.assertEqual(metadata, expected)

    @responses.activate
    def test_download_egg(self):
        # Given
        name = 'numpy'
        version = '1.8.0-1'
        python_tag = 'py3'
        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)
        body = 'data'
        sha256 = hashlib.sha256(body.encode('ascii')).hexdigest()

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.eggs.download.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                    name=name,
                    version=version,
                    python_tag=python_tag,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
        )
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.artefacts.eggs.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                    name=name,
                    version=version,
                    python_tag=python_tag,
                ),
            ),
            body=json.dumps({'sha256': sha256}),
            status=200,
            content_type='application/json',
        )

        # When
        platform.download_egg(
            python_tag, name, version, destination=self.temp_dir)

        # Then
        filename = os.path.join(
            self.temp_dir, '{0}-{1}.egg'.format(name, version))
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertTrue(os.path.isfile(filename),
                        msg='Expected file {0!r} to exist'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

        with open(filename) as fh:
            self.assertEqual(fh.read(), 'data')

    @responses.activate
    def test_download_egg_invalid_sha(self):
        # Given
        name = 'numpy'
        version = '1.8.0-1'
        python_tag = 'py3'
        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)
        body = 'data'
        sha256 = 'abc123'

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.eggs.download.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                    name=name,
                    version=version,
                    python_tag=python_tag,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
        )
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.artefacts.eggs.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                    name=name,
                    version=version,
                    python_tag=python_tag,
                ),
            ),
            body=json.dumps({'sha256': sha256}),
            status=200,
            content_type='application/json',
        )

        # When
        with self.assertRaises(ChecksumMismatchError):
            platform.download_egg(
                python_tag, name, version, destination=self.temp_dir)

        # Then
        filename = os.path.join(
            self.temp_dir, '{0}-{1}.egg'.format(name, version))
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

    @responses.activate
    def test_iter_download_egg(self):
        # Given
        name = 'numpy'
        version = '1.8.0-1'
        python_tag = 'py3'
        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)
        body = 'data'
        sha256 = hashlib.sha256(body.encode('ascii')).hexdigest()
        content_length = len(body)

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.eggs.download.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                    name=name,
                    version=version,
                    python_tag=python_tag,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(content_length),
            },
        )
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.artefacts.eggs.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                    name=name,
                    version=version,
                    python_tag=python_tag,
                ),
            ),
            body=json.dumps({'sha256': sha256}),
            status=200,
            content_type='application/json',
        )

        # When
        length, iterator = platform.iter_download_egg(
            python_tag, name, version, destination=self.temp_dir)

        # Then
        self.assertEqual(length, content_length)
        filename = os.path.join(
            self.temp_dir, '{0}-{1}.egg'.format(name, version))
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))

        next(iterator)

        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))
        self.assertTrue(
            os.path.isfile(temp_filename),
            msg='Expected file {0!r} to exist'.format(temp_filename))

        with self.assertRaises(StopIteration):
            next(iterator)

        self.assertTrue(os.path.isfile(filename),
                        msg='Expected file {0!r} to exist'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

        with open(filename) as fh:
            self.assertMultiLineEqual(fh.read(), body)

    @responses.activate
    def test_iter_download_egg_bad_shasum(self):
        # Given
        name = 'numpy'
        version = '1.8.0-1'
        python_tag = 'py3'
        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)
        body = 'data'
        sha256 = 'xxxxxx'
        content_length = len(body)

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.eggs.download.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                    name=name,
                    version=version,
                    python_tag=python_tag,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(content_length),
            },
        )
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.artefacts.eggs.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                    name=name,
                    version=version,
                    python_tag=python_tag,
                ),
            ),
            body=json.dumps({'sha256': sha256}),
            status=200,
            content_type='application/json',
        )

        # When
        length, iterator = platform.iter_download_egg(
            python_tag, name, version, destination=self.temp_dir)

        # Then
        self.assertEqual(length, content_length)
        filename = os.path.join(
            self.temp_dir, '{0}-{1}.egg'.format(name, version))
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))

        next(iterator)

        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))
        self.assertTrue(
            os.path.isfile(temp_filename),
            msg='Expected file {0!r} to exist'.format(temp_filename))

        with self.assertRaises(ChecksumMismatchError):
            next(iterator)

        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

    @responses.activate
    def test_delete_egg(self):
        # Given
        name = 'numpy'
        version = '1.8.0-1'
        python_tag = 'py3'

        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)

        responses.add(
            responses.DELETE,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.eggs.delete.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                    name=name,
                    version=version,
                    python_tag=python_tag,
                ),
            ),
        )

        # When
        platform.delete_egg(python_tag, name, version)

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        self.assertEqual(request.method, "DELETE")

    @responses.activate
    def test_upload_egg(self):
        # Given
        name = 'numpy'
        version = '1.8.0'
        build = 1
        data = 'numpy!'
        filepath = os.path.join(
            self.temp_dir, '{0}-{1}-{2}.egg'.format(name, version, build))

        with open(filepath, 'w') as fh:
            fh.write(data)

        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)

        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.eggs.upload.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                ),
            ),
        )

        # When
        platform.upload_egg(filepath)

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        json_data = self._parse_multipart_data(request.body, request.headers)

        self.assertJsonValid(json_data, 'upload_egg.json')
        self.assertRegexpMatches(request.url, r'^.*?\?.*?overwrite=False')
        self.assertRegexpMatches(request.url, r'^.*?\?.*?enabled=True')

    @responses.activate
    def test_upload_egg_unicode_filename(self):
        """
        Test for enthought/hatcher#113 to exhibit kennethreitz/requests#2411
        under Python 2.x.
        """
        # Given
        name = 'numpy'
        version = '1.8.0'
        build = 1
        data = 'numpy!'
        filepath = os.path.join(
            self.temp_dir, '{0}-{1}-{2}.egg'.format(name, version, build))
        if not isinstance(filepath, six.text_type):
            filepath = filepath.decode('ascii')

        with open(filepath, 'w') as fh:
            fh.write(data)

        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)

        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.eggs.upload.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                ),
            ),
        )

        # When
        platform.upload_egg(filepath)

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        json_data = self._parse_multipart_data(request.body, request.headers)

        # Test for enthought/hatcher#113
        for line in request.body.decode('utf-8').splitlines():
            filename_match = BODY_FILENAME_RE.match(line)
            if filename_match is not None:
                break
        self.assertIsNotNone(filename_match)
        self.assertEqual(filename_match.group(1), os.path.basename(filepath))

        self.assertJsonValid(json_data, 'upload_egg.json')
        self.assertRegexpMatches(
            request.url, r'^.*?\?overwrite=False&enabled=True$')

    @responses.activate
    def test_upload_egg_force(self):
        # Given
        name = 'numpy'
        version = '1.8.0'
        build = 1
        data = 'numpy!'
        filepath = os.path.join(
            self.temp_dir, '{0}-{1}-{2}.egg'.format(name, version, build))

        with open(filepath, 'w') as fh:
            fh.write(data)

        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)

        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.eggs.upload.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                ),
            ),
        )

        # When
        platform.upload_egg(filepath, overwrite=True)

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        json_data = self._parse_multipart_data(request.body, request.headers)
        self.assertJsonValid(json_data, 'upload_egg.json')
        self.assertRegexpMatches(
            request.url, r'^.*?\?overwrite=True&enabled=True$')

    @responses.activate
    def test_upload_egg_force_disabled(self):
        # Given
        name = 'numpy'
        version = '1.8.0'
        build = 1
        data = 'numpy!'
        filepath = os.path.join(
            self.temp_dir, '{0}-{1}-{2}.egg'.format(name, version, build))

        with open(filepath, 'w') as fh:
            fh.write(data)

        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)

        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.eggs.upload.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                ),
            ),
        )

        # When
        platform.upload_egg(filepath, overwrite=True, enabled=False)

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        json_data = self._parse_multipart_data(request.body, request.headers)
        self.assertJsonValid(json_data, 'upload_egg.json')
        self.assertRegexpMatches(
            request.url, r'^.*?\?overwrite=True&enabled=False$')

    @responses.activate
    def test_upload_egg_disabled(self):
        # Given
        name = 'numpy'
        version = '1.8.0'
        build = 1
        data = 'numpy!'
        filepath = os.path.join(
            self.temp_dir, '{0}-{1}-{2}.egg'.format(name, version, build))

        with open(filepath, 'w') as fh:
            fh.write(data)

        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)

        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.eggs.upload.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                ),
            ),
        )

        # When
        platform.upload_egg(filepath, enabled=False)

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        json_data = self._parse_multipart_data(request.body, request.headers)
        self.assertJsonValid(json_data, 'upload_egg.json')
        self.assertRegexpMatches(
            request.url, r'^.*?\?overwrite=False&enabled=False$')

    @responses.activate
    def test_list_runtimes(self):
        # Given
        index = {
            'python': {
                '2.7.3': {
                    '1': {
                        'build': 1,
                        'file_format': 'zip',
                        'filename': 'python_runtime_2.7.3_2.0.0.dev1-c9fa3fa_rh5-64_1.zip',  # noqa
                        'language': 'python',
                        'platform': 'rh5-64',
                        'sha256': '9713a9c3a35ab044133efa65233117eb11f2fabf413453dfc15dbc2dca23b858',  # noqa
                        'version': '2.7.3',
                        'build_system_version': '2.0.0.dev1-c9fa3fa'
                    },
                    '2': {
                        'build': 2,
                        'file_format': 'zip',
                        'filename': 'python_runtime_2.7.3_2.0.0.dev1-3fac9fa_rh5-64_2.zip',  # noqa
                        'language': 'python',
                        'platform': 'rh5-64',
                        'sha256': 'eb11f2fabf413453dfc15dbc2dca23b8589713a9c3a35ab044133efa65233117',  # noqa
                        'version': '2.7.3',
                        'build_system_version': '2.0.0.dev1-3fac9fa'
                    },
                },
            },
        }
        expected = ['python_runtime_2.7.3_2.0.0.dev1-c9fa3fa_rh5-64_1.zip',
                    'python_runtime_2.7.3_2.0.0.dev1-3fac9fa_rh5-64_2.zip']
        platform_name = 'rh5-64'
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.indices.runtimes.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                )
            ),
            body=json.dumps(index),
            status=200,
            content_type='application/json',
        )

        platform = self.repository.platform(platform_name)

        # When
        metadata = platform.list_runtimes()

        # Then
        self.assertEqual(list(sorted(metadata)), list(sorted(expected)))

    @responses.activate
    def test_runtime_index(self):
        # Given
        given_index = {
            'python': {
                '2.7.3': {
                    '1': {
                        'build': 1,
                        'file_format': 'zip',
                        'filename': 'python_runtime_2.7.3_2.0.0.dev1-c9fa3fa_rh5-64_1.zip',  # noqa
                        'language': 'python',
                        'platform': 'rh5-64',
                        'sha256': '9713a9c3a35ab044133efa65233117eb11f2fabf413453dfc15dbc2dca23b858',  # noqa
                        'version': '2.7.3',
                        'build_system_version': '2.0.0.dev1-c9fa3fa'
                    },
                    '2': {
                        'build': 2,
                        'file_format': 'zip',
                        'filename': 'python_runtime_2.7.3_2.0.0.dev1-3fac9fa_rh5-64_2.zip',  # noqa
                        'language': 'python',
                        'platform': 'rh5-64',
                        'sha256': 'eb11f2fabf413453dfc15dbc2dca23b8589713a9c3a35ab044133efa65233117',  # noqa
                        'version': '2.7.3',
                        'build_system_version': '2.0.0.dev1-3fac9fa'
                    },
                },
            },
        }
        platform_name = 'rh5-64'
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.indices.runtimes.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                )
            ),
            body=json.dumps(given_index),
            status=200,
            content_type='application/json',
        )

        platform = self.repository.platform(platform_name)

        # When
        obtained_index = platform.runtime_index()

        # Then
        self.assertEqual(dict(obtained_index), dict(given_index))

    @responses.activate
    def test_runtime_metadata(self):
        # Given
        language = 'python'
        python_tag = 'cp27'
        version = '2.7.3'
        build = 1
        full_version = '{0}-{1}'.format(version, build)
        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)
        filename = 'python_runtime_2.7.3_2.0.0.dev1-c9fa3fa_win-32_1.zip'
        sha256 = "9713a9c3a35ab044133efa65233117eb11f2fabf413453dfc15dbc2dca23b858"  # noqa

        expected = {
            "build": build,
            "file_format": "zip",
            "filename": filename,
            "language": language,
            "platform": platform_name,
            "sha256": sha256,
            "version": version,
            "build_system_version": "2.0.0.dev1-c9fa3fa"
        }

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.artefacts.runtimes.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform='rh5-64',
                    python_tag=python_tag,
                    version=full_version,
                ),
            ),
            body=json.dumps(expected),
            status=200,
            content_type='application/json',
        )

        # When
        metadata = platform.runtime_metadata(python_tag, full_version)

        # Then
        self.assertEqual(metadata, expected)

    @responses.activate
    def test_download_runtime(self):
        # Given
        python_tag = 'cp27'
        version = '2.7.3-1'
        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)
        filename = 'python_runtime_2.7.3_2.0.0.dev1-c9fa3fa_win-32_1.zip'
        body = 'data'
        sha256 = hashlib.sha256(body.encode('ascii')).hexdigest()

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.runtimes.download.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform='rh5-64',
                    python_tag=python_tag,
                    version=version,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(len(body)),
                'Content-Disposition': 'attachment; filename="{0}"'.format(
                    filename)
            },
        )
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.artefacts.runtimes.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform='rh5-64',
                    python_tag=python_tag,
                    version=version,
                ),
            ),
            body=json.dumps({'sha256': sha256}),
            status=200,
            content_type='application/json',
        )

        # When
        platform.download_runtime(
            python_tag, version, destination=self.temp_dir)

        # Then
        filename = os.path.join(self.temp_dir, filename)
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertTrue(os.path.isfile(filename),
                        msg='Expected file {0!r} to exist'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

        with open(filename) as fh:
            self.assertEqual(fh.read(), 'data')

    @responses.activate
    def test_download_runtime_bad_sha(self):
        # Given
        python_tag = 'cp27'
        version = '2.7.3-1'
        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)
        filename = 'python_runtime_2.7.3_2.0.0.dev1-c9fa3fa_win-32_1.zip'
        body = 'data'
        sha256 = 'abc123efd'

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.runtimes.download.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform='rh5-64',
                    python_tag=python_tag,
                    version=version,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(len(body)),
                'Content-Disposition': 'attachment; filename="{0}"'.format(
                    filename)
            },
        )
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.artefacts.runtimes.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform='rh5-64',
                    python_tag=python_tag,
                    version=version,
                ),
            ),
            body=json.dumps({'sha256': sha256}),
            status=200,
            content_type='application/json',
        )

        # When
        with self.assertRaises(ChecksumMismatchError):
            platform.download_runtime(
                python_tag, version, destination=self.temp_dir)

        # Then
        filename = os.path.join(self.temp_dir, filename)
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

    @responses.activate
    def test_iter_download_runtime(self):
        # Given
        python_tag = 'cp27'
        version = '2.7.3-1'
        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)
        filename = 'python_runtime_2.7.3_2.0.0.dev1-c9fa3fa_win-32_1.zip'
        body = 'data'
        sha256 = hashlib.sha256(body.encode('ascii')).hexdigest()
        content_length = len(body)

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.runtimes.download.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform='rh5-64',
                    python_tag=python_tag,
                    version=version,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(content_length),
                'Content-Disposition': 'attachment; filename="{0}"'.format(
                    filename)
            },
        )
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.artefacts.runtimes.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform='rh5-64',
                    python_tag=python_tag,
                    version=version,
                ),
            ),
            body=json.dumps({'sha256': sha256}),
            status=200,
            content_type='application/json',
        )

        # When
        length, iterator = platform.iter_download_runtime(
            python_tag, version, destination=self.temp_dir)

        # Then
        self.assertEqual(length, content_length)
        filename = os.path.join(self.temp_dir, filename)
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

        next(iterator)
        self.assertTrue(
            os.path.isfile(temp_filename),
            msg='Expected file {0!r} to exist'.format(temp_filename))
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))

        with self.assertRaises(StopIteration):
            next(iterator)

        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))
        self.assertTrue(
            os.path.isfile(filename),
            msg='Expected file {0!r} to exist'.format(filename))

        with open(filename) as fh:
            self.assertMultiLineEqual(fh.read(), body)

    @responses.activate
    def test_iter_download_runtime_bad_sha(self):
        # Given
        python_tag = 'cp27'
        version = '2.7.3-1'
        platform_name = 'rh5-64'
        platform = self.repository.platform(platform_name)
        filename = 'python_runtime_2.7.3_2.0.0.dev1-c9fa3fa_win-32_1.zip'
        body = 'data'
        sha256 = 'abc123efd'
        content_length = len(body)

        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.runtimes.download.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform='rh5-64',
                    python_tag=python_tag,
                    version=version,
                ),
            ),
            body=body,
            status=200,
            content_type='application/octet-stream',
            adding_headers={
                'Content-Length': str(content_length),
                'Content-Disposition': 'attachment; filename="{0}"'.format(
                    filename)
            },
        )
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.artefacts.runtimes.format(
                    organization_name='enthought',
                    repository_name='free',
                    platform='rh5-64',
                    python_tag=python_tag,
                    version=version,
                ),
            ),
            body=json.dumps({'sha256': sha256}),
            status=200,
            content_type='application/json',
        )

        # When
        length, iterator = platform.iter_download_runtime(
            python_tag, version, destination=self.temp_dir)

        # Then
        self.assertEqual(length, content_length)
        filename = os.path.join(self.temp_dir, filename)
        temp_filename = '{0}.hatcher-partial'.format(filename)
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))
        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))

        next(iterator)
        self.assertTrue(
            os.path.isfile(temp_filename),
            msg='Expected file {0!r} to exist'.format(temp_filename))
        self.assertFalse(
            os.path.isfile(filename),
            msg='Did not expect file {0!r} to exist yet'.format(filename))

        with self.assertRaises(ChecksumMismatchError):
            next(iterator)

        self.assertFalse(
            os.path.isfile(temp_filename),
            msg='Did not expect file {0!r} to exist yet'.format(temp_filename))
        self.assertFalse(
            os.path.isfile(filename),
            msg='Expected file {0!r} to exist'.format(filename))

    @responses.activate
    def test_upload_runtime(self):
        # Given
        filename = 'python_runtime_2.7.3_2.0.0.dev1-c9fa3fa_win-32_1.zip'
        data = 'python'
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as fh:
            fh.write(data)

        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.runtimes.upload.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform='win-32',
                ),
            ),
        )

        # When
        self.repository.upload_runtime(filepath)

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        json_data = self._parse_multipart_data(request.body, request.headers)
        self.assertJsonValid(json_data, 'upload_runtime.json')
        self.assertRegexpMatches(request.url, r'^.*?\?overwrite=False$')

    @responses.activate
    def test_upload_runtime_force(self):
        # Given
        filename = 'python_runtime_2.7.3_2.0.0.dev1-c9fa3fa_win-32_1.zip'
        data = 'python'
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as fh:
            fh.write(data)

        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.runtimes.upload.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform='win-32',
                ),
            ),
        )

        # When
        self.repository.upload_runtime(filepath, overwrite=True)

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        json_data = self._parse_multipart_data(request.body, request.headers)
        self.assertJsonValid(json_data, 'upload_runtime.json')
        self.assertRegexpMatches(request.url, r'^.*?\?overwrite=True$')

    @responses.activate
    def test_get_app_metadata(self):
        # Given
        python_tag = 'cp27'
        expected = {
            'id': 'mayavi',
            'version': '1.0',
            'other_key': 'value',
            'python_tag': 'cp27',
        }
        version = expected['version'] + '-1'
        platform_name = 'rh5-64'
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.metadata.artefacts.apps.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                    python_tag=python_tag,
                    app_id='mayavi',
                    version=version,
                )
            ),
            body=json.dumps(expected),
            status=200,
            content_type='application/json',
        )

        platform = self.repository.platform(platform_name)

        # When
        metadata = platform.app_metadata(python_tag, 'mayavi', version)

        # Then
        self.assertEqual(metadata, expected)

    @responses.activate
    def test_upload_app(self):
        # Given
        filename = 'mayavi.yaml'
        data = 'platform: "rh5-64"'
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as fh:
            fh.write(data)

        platform_name = 'rh5-64'
        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.apps.upload.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                ),
            ),
        )

        # When
        self.repository.upload_app(filepath)

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        json_data = self._parse_multipart_data(request.body, request.headers)
        self.assertJsonValid(json_data, 'upload_app.json')
        self.assertRegexpMatches(request.url, r'^.*?\?overwrite=False$')

    @responses.activate
    def test_upload_app_force(self):
        # Given
        filename = 'mayavi.yaml'
        data = 'platform: "rh5-64"'
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as fh:
            fh.write(data)

        platform_name = 'rh5-64'
        responses.add(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.apps.upload.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                ),
            ),
        )

        # When
        self.repository.upload_app(filepath, overwrite=True)

        # Then
        self.assertEqual(len(responses.calls), 1)
        call, = responses.calls
        request, response = call
        json_data = self._parse_multipart_data(request.body, request.headers)
        self.assertJsonValid(json_data, 'upload_app.json')
        self.assertRegexpMatches(request.url, r'^.*?\?overwrite=True$')

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
        expected = [(app, '{0}-{1}'.format(version, build), python_tag)
                    for python_tag, apps in given_index.items()
                    for app, versions in apps.items()
                    for version, builds in versions.items()
                    for build, metadata in builds.items()]
        platform_name = 'rh5-64'
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.indices.apps.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                )
            ),
            body=json.dumps(given_index),
            status=200,
            content_type='application/json',
        )

        platform = self.repository.platform(platform_name)

        # When
        metadata = platform.list_apps()

        # Then
        self.assertEqual(list(sorted(metadata)), list(sorted(expected)))

    @responses.activate
    def test_app_index(self):
        # Given
        given_index = {
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
                '4.6': {
                    '1': {
                        'name': 'Mayavi demo',
                        'description': 'Simple mayavi demo',
                        'python_tag': 'cp27',
                    },
                },
            },
        }
        platform_name = 'rh5-64'
        responses.add(
            responses.GET,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.indices.apps.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                    platform=platform_name,
                )
            ),
            body=json.dumps(given_index),
            status=200,
            content_type='application/json'
        )

        platform = self.repository.platform(platform_name)

        # When
        obtained_index = platform.app_index()

        # Then
        self.assertEqual(dict(obtained_index), dict(given_index))

    @responses.activate
    def test_reindex(self):
        # Given
        egg1 = make_testing_egg(self.temp_dir, name='egg1')
        duplicate_egg1 = make_testing_egg(self.temp_dir2, name='egg1')
        egg2 = make_testing_egg(self.temp_dir, name='egg2')
        egg3 = make_testing_egg(self.temp_dir, name='egg3', python_tag=None)
        eggs_to_enable = [egg1.path, duplicate_egg1.path, egg2.path, egg3.path]

        _eggs_entry = lambda egg: {
            'name': egg.name,
            'version': '{0}-{1}'.format(egg.version, egg.build),
            'python_tag': (egg.python_tag
                           if egg.python_tag is not None else 'none'),
        }

        expected = [
            _eggs_entry(egg1),
            _eggs_entry(egg2),
            _eggs_entry(egg3),
        ]

        self.json_str = None

        def callback(request):
            self.json_str = request.body
            return (202, {}, '')

        responses.add_callback(
            responses.POST,
            '{scheme}://{host}{path}'.format(
                scheme=self.url_handler.scheme,
                host=self.url_handler.host,
                path=URLS.data.re_index.eggs.format(
                    organization_name=self.repository.organization_name,
                    repository_name=self.repository.name,
                )
            ),
            callback=callback,
        )

        # When
        self.repository.reindex(eggs_to_enable)

        # Then
        self.assertJsonValid(self.json_str, 'enable_eggs_for_indexing.json')
        json_data = json.loads(self.json_str)
        self.assertEqual(list(json_data.keys()), ['eggs'])
        eggs = list(
            sorted(
                json_data['eggs'],
                key=lambda i: tuple(i.items())
            )
        )
        self.assertEqual(eggs, expected)
