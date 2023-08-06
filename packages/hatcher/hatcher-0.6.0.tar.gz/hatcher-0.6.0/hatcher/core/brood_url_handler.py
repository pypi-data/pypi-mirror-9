# Canopy product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import

import hashlib
import json
import os
import re

import requests
from six.moves.urllib import parse as urlparse
from six import BytesIO

from hatcher.errors import ChecksumMismatchError, MissingFilenameError
from .utils import compute_sha256, hatcher_user_agent


FILENAME_FROM_CONTENT_DISPOSITION = re.compile(r'^.*?filename="(\S+)"')


class BroodURLHandler(object):
    """Low level handling of the interface between the Hatcher API and the
    Brood API.

    """

    api_root = '/api/v0/json'

    def __init__(self, url, auth=None, verify_ssl=True):
        """Create a BroodURLHandler.

        Parameters
        ----------
        url : str
            The root URL of a brood server in the form <scheme>://<host>
        auth : tuple
            A two-tuple of the form (username, password)
        verify_ssl : bool
            ``False`` to disable SSL certificate verification (default on)

        """
        parsed_url = urlparse.urlparse(url)
        if parsed_url.netloc == '':
            parsed_url = urlparse.urlparse('//{0}'.format(url))

        self.scheme = parsed_url.scheme or 'http'
        self.host = parsed_url.netloc
        self.verify_ssl = verify_ssl
        self._session = requests.Session()
        self._session.verify = self.verify_ssl
        self._session.auth = auth
        self._session.headers['User-Agent'] = hatcher_user_agent()

    def _build_url(self, path, query=None):
        """Construct a full URL for a request using the configured scheme and
        host.

        Parameters
        ----------
        path : str
            The resource path to use in the URL
        query : dict
            A dictionary of query parameters.

        """
        if query is not None:
            query = urlparse.urlencode(query)
        return urlparse.urlunsplit(
            (
                self.scheme,
                self.host,
                path,
                query,
                None
            ),
        )

    def _request(self, method, url, **kwargs):
        """Perform a request by calling ``method`` with arguments ``url`` and
        ``**kwargs``.

        Parameters
        ----------
        method : callable
            The HTTP request method to call on the ``requests`` ``Session``.
        url : str
            The full URL (including any query parameters) to make the
            request against.
        kwargs : dict
            Keyword arguments to pass through to ``requests``.

        """
        response = method(url, **kwargs)
        response.raise_for_status()
        return response

    def get(self, path):
        """Issue a GET request to the given ``path``.

        Parameters
        ----------
        path : str
            The resource path to use in the URL

        """
        url = self._build_url(path)
        self._request(self._session.get, url)

    def delete(self, path, force=False):
        """Issue a DELETE request for the object referenced by ``path``.

        Parameters
        ----------
        path : str
            The resource path to use in the URL
        force : bool
            Force deletion of the resource if it would otherwise fail.

        """
        url = self._build_url(path, query={'force': force})
        self._request(self._session.delete, url)

    def put(self, path, data=None):
        """Issue a PUT request to the given ``path`` containing the given json
        ``data``.

        Parameters
        ----------
        path : str
            The resource path to use in the URL
        data : dict
            A dictionary of data to be passed as JSON-encoded data to
            the request.

        """
        url = self._build_url(path)
        if data is None:
            kwargs = {}
        else:
            kwargs = {
                'data': json.dumps(data),
                'headers': {'Content-Type': 'application/json'},
            }
        self._request(self._session.put, url, **kwargs)

    def post(self, path, data):
        """Issue a POST request to the given ``path`` containing the given json
        ``data``.

        Parameters
        ----------
        path : str
            The resource path to use in the URL
        data : dict
            A dictionary of data to be passed as JSON-encoded data to
            the request.

        """
        url = self._build_url(path)
        return self._request(self._session.post, url, data=json.dumps(data),
                             headers={'Content-Type': 'application/json'})

    def upload(self, path, data, filename, overwrite=False, enabled=None):
        """Issue a POST request to the given ``path`` containing the given json
        ``data`` and a file..

        Parameters
        ----------
        path : str
            The resource path to use in the URL
        data : dict
            A dictionary of metadata to be passed as JSON-encoded data to
            the request.
        filename : str
            Path to the file to upload.
        overwrite : bool
            Overwrite an existing artefact specified by the same metadata.
        enabled : bool
            Only valid for egg uploads.  If ``False``, egg will not be
            indexed on upload.

        """
        query = [('overwrite', overwrite)]
        if enabled is not None:
            query.append(('enabled', enabled))
        url = self._build_url(path, query=query)
        with open(filename, 'rb') as fh:
            files = {'file': fh,
                     'data': ('', BytesIO(json.dumps(data).encode('utf-8')),
                              'application/json; charset=UTF-8', {})}
            self._request(self._session.post, url, files=files)

    def iter_download(self, path, destination_directory, expected_sha256,
                      filename=None):
        """Download the file specified by ``path`` and save it in the
        ``destination_directory``.

        This method returns a tuple of (content_length, iterator).  The
        ``content_length`` is the total size of the download.  The
        ``iterator`` yields the size of each chunk as it is downloaded.

        Parameters
        ----------
        path : str
            The resource path to use in the URL
        destination_directory : str
            The directory in which to save the downloaded file.
        expected_sha256 : str
            The expected SHA256 sum of the downloaded file.
        filename : str
            Optional name for the file being saved.  If it is not
            provided, the filename specified in the
            ``Content-Disposition`` header of the response will be used.

        """
        url = self._build_url(path)
        response = self._request(self._session.get, url, stream=True)
        if filename is None:
            content_disposition = response.headers['Content-Disposition']
            match = FILENAME_FROM_CONTENT_DISPOSITION.match(
                content_disposition)
            if match is not None:
                filename = match.group(1)
            else:
                raise MissingFilenameError(
                    "No 'Content-Disposition' header and no filename "
                    "explicitly given")

        content_length = int(response.headers.get('Content-Length', 0))
        destination_file = os.path.join(destination_directory, filename)
        if os.path.isfile(destination_file):
            existing_sha256 = compute_sha256(destination_file)
            if existing_sha256 == expected_sha256:
                def empty_save_iterator():
                    yield content_length
                    response.close()
                return content_length, empty_save_iterator()

        def save_iterator(dest_path, response):
            shasum = hashlib.sha256()
            temp_dest = '{}.hatcher-partial'.format(dest_path)
            with open(temp_dest, 'wb') as fp:
                for block in response.iter_content(chunk_size=65536):
                    shasum.update(block)
                    fp.write(block)
                    yield len(block)

            actual_sha256 = shasum.hexdigest()
            if actual_sha256 != expected_sha256:
                os.unlink(temp_dest)
                raise ChecksumMismatchError(
                    'Checksum failed for {!r}'.format(dest_path))
            else:
                if os.path.exists(dest_path):
                    os.unlink(dest_path)
                os.rename(temp_dest, dest_path)

        return (
            content_length,
            save_iterator(dest_path=destination_file, response=response),
        )

    def download_file(self, path, destination_directory, expected_sha256,
                      filename=None):
        """Download the file specified by ``path`` and save it in the
        ``destination_directory``.

        Parameters
        ----------
        path : str
            The resource path to use in the URL
        destination_directory : str
            The directory in which to save the downloaded file.
        expected_sha256 : str
            The expected SHA256 sum of the downloaded file.
        filename : str
            Optional name for the file being saved.  If it is not
            provided, the filename specified in the
            ``Content-Disposition`` header of the response will be used.

        """
        length, iterator = self.iter_download(
            path, destination_directory, expected_sha256, filename=filename)
        for chunk_size in iterator:
            pass

    def get_json(self, path):
        """Get the JOSN payload at ``path``.

        Parameters
        ----------
        path : str
            The resource path to use in the URL

        """
        url = self._build_url(path)
        response = self._request(self._session.get, url)
        return response.json()
