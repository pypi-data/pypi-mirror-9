# Canopy product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import

import requests

from .url_templates import URLS


class Team(object):

    def __init__(self, organization_name, name, url_handler):
        self.organization_name = organization_name
        self.name = name
        self._url_handler = url_handler

    def __repr__(self):
        return '<{cls} organization={organization!r}, team={team!r}>'.format(
            cls=type(self).__name__,
            organization=self.organization_name,
            team=self.name,
        )

    def _query_access(self, path):
        """Perform a GET request on the given ``path``. Return ``True`` if the
        request was a success, ``False`` if the response is ``404 NOT FOUND``
        or raise the original error otherwise.

        """
        try:
            self._url_handler.get(path)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return False
            raise
        else:
            return True

    #### Basic Team Management ################################################

    def delete(self):
        """Delete this team.

        """
        path = URLS.admin.teams.format(
            organization_name=self.organization_name,
            team_name=self.name,
        )
        self._url_handler.delete(path)

    def metadata(self):
        """Get the metadata for this team.

        """
        path = URLS.admin.teams.format(
            organization_name=self.organization_name,
            team_name=self.name,
        )
        return self._url_handler.get_json(path)

    #### Team Repository Access Management ####################################

    def list_repositories(self):
        """List all repositories to which this team has access.

        """
        path = URLS.admin.teams.repositories.format(
            organization_name=self.organization_name,
            team_name=self.name,
        )
        repositories = self._url_handler.get_json(path)
        return repositories['repositories']

    def add_repository(self, repository):
        """Add a repository to this team.

        Parameters
        ----------
        repository : hatcher.repository.Repository
            The repository to add to the team.

        """
        path = URLS.admin.teams.repositories.query.format(
            organization_name=self.organization_name,
            team_name=self.name,
            repository_name=repository.name
        )
        self._url_handler.put(path)

    def remove_repository(self, repository):
        """Remove a repository from this team.

        Parameters
        ----------
        repository : hatcher.repository.Repository
            The repository to add to the team.

        """
        path = URLS.admin.teams.repositories.query.format(
            organization_name=self.organization_name,
            team_name=self.name,
            repository_name=repository.name
        )
        self._url_handler.delete(path)

    def query_repository_access(self, repository):
        """Query if this team has access to a repository.

        Parameters
        ----------
        repository : hatcher.repository.Repository
            The repository to add to the team.

        Returns
        -------
        access : bool
            ``True`` if the team has access to the repository, ``False``
            otherwise.

        """
        path = URLS.admin.teams.repositories.query.format(
            organization_name=self.organization_name,
            team_name=self.name,
            repository_name=repository.name
        )
        return self._query_access(path)

    #### Team User Access Management ##########################################

    def _team_member_url(self, user):
        """Create the URL for a particular team member endpoint

        Parameters
        ----------
        user : hatcher.user.User

        """
        return URLS.admin.teams.members.query.format(
            organization_name=self.organization_name,
            team_name=self.name,
            email=user.email,
        )

    def list_users(self):
        """List all users in this team.

        """
        path = URLS.admin.teams.members.format(
            organization_name=self.organization_name,
            team_name=self.name,
        )
        members = self._url_handler.get_json(path)
        return members['members']

    def add_user(self, user):
        """Add a user to this team.

        Parameters
        ----------
        user : hatcher.user.User
            The user to add to this team.

        """
        path = URLS.admin.teams.members.query.format(
            organization_name=self.organization_name,
            team_name=self.name,
            email=user.email,
        )
        self._url_handler.put(path)

    def remove_user(self, user):
        """Remove a user from this team.

        Parameters
        ----------
        user : hatcher.user.User
            The user to remove from this team.

        """
        path = URLS.admin.teams.members.query.format(
            organization_name=self.organization_name,
            team_name=self.name,
            email=user.email,
        )
        self._url_handler.delete(path)

    def query_user_access(self, user):
        """Query if a user is a member of this team.

        Parameters
        ----------
        user : hatcher.user.User
            The user to whose access to query.

        """
        path = URLS.admin.teams.members.query.format(
            organization_name=self.organization_name,
            team_name=self.name,
            email=user.email,
        )
        return self._query_access(path)
