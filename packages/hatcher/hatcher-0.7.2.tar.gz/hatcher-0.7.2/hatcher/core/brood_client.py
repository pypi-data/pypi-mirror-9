# Canopy product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import

from .brood_url_handler import BroodURLHandler
from .organization import Organization
from .url_templates import URLS


class BroodClient(object):
    """``BroodClient`` is the top level entry point into the ``hatcher``
    API.

    """

    def __init__(self, url_handler):
        self._url_handler = url_handler

    @classmethod
    def from_url(cls, url, auth=None, verify_ssl=True):
        """Create a ``BroodClient`` from a Brood URL.

        """
        url_handler = BroodURLHandler(url, auth=auth, verify_ssl=verify_ssl)
        return cls(url_handler=url_handler)

    def create_organization(self, name, description):
        """Create a new organization called ``name`` with the description
        ``description``.

        Parameters
        ----------
        name : str
            The name of the organization.
        description : str
            The description of the organization.

        Returns :class:`~hatcher.core.organization.Organization`

        """
        data = {
            'name': name,
            'description': description,
        }
        path = URLS.admin.organizations.format()
        self._url_handler.post(path, data)
        return self.organization(name)

    def organization(self, name):
        """Get an existing organization.

        Parameters
        ----------
        name : str
            The name of the organization.

        Returns :class:`~hatcher.core.organization.Organization`

        """
        return Organization(name, url_handler=self._url_handler)

    def list_organizations(self):
        """List all organizations in the brood server.

        """
        path = URLS.admin.organizations.format()
        data = self._url_handler.get_json(path)
        return list(sorted(data['organizations']))

    def create_api_token(self, name):
        """Create a new API token for the current user.

        Parameters
        ----------
        name : str
            The name for the new token.

        Returns
        -------
        token : dict
            Dict containing the token and its name.

        """
        path = URLS.tokens.api.format()
        data = {'name': name}
        response = self._url_handler.post(path, data)
        return response.json()

    def delete_api_token(self, name):
        """Delete the user's named API token.

        Parameters
        ----------
        name : str
            The name of the token to delete.

        """
        path = URLS.tokens.api.delete.format(name=name)
        self._url_handler.delete(path)

    def list_api_tokens(self):
        """List the metadata of user's API tokens.

        .. note::
            This does not list the actual token that can be used for
            authentication, just the metadata ``name``, ``created`` and
            ``last_used``.

        Returns
        -------
        tokens : list
            List of metadata for all of the user's active tokens.

        """
        path = URLS.tokens.api.format()
        tokens = self._url_handler.get_json(path)
        return tokens['tokens']

    def list_platforms(self):
        """List all platforms supported by the Brood server.

        Returns
        -------
        platforms : list
            List of platform names.

        """
        path = URLS.metadata.platforms.format()
        platforms = self._url_handler.get_json(path)
        return platforms['platforms']

    def list_python_tags(self, list_all=False):
        """List PEP425 Python Tags supported by the Brood server.

        Parameters
        ----------
        list_all : bool
            If ``False`` (default), will only list the tags that
            correspond to an actual Python implementation and version.
            If ``True``, list all possible tags.

        Returns
        -------
        tags : list
            List of Python tags.

        """
        if list_all:
            path = URLS.metadata.python_tags.all.format()
        else:
            path = URLS.metadata.python_tags.format()
        python_tags = self._url_handler.get_json(path)
        return python_tags['python_tags']
