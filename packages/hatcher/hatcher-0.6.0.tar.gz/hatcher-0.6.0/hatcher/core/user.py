# Canopy product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import

from .url_templates import URLS


class User(object):

    def __init__(self, organization_name, email, url_handler):
        self.organization_name = organization_name
        self.email = email
        self._url_handler = url_handler

    def __repr__(self):
        return '<{cls} organization={organization!r}, email={email!r}>'.format(
            cls=type(self).__name__,
            organization=self.organization_name,
            email=self.email,
        )

    def delete(self):
        """Delete this user from the brood server.

        """
        path = URLS.admin.users.metadata.format(
            organization_name=self.organization_name,
            email=self.email,
        )
        self._url_handler.delete(path)

    def metadata(self):
        """Get the user's metadata.

        """
        path = URLS.admin.users.metadata.format(
            organization_name=self.organization_name,
            email=self.email,
        )
        return self._url_handler.get_json(path)
