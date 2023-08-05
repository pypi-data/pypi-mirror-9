# Canopy product code
#
# (C) Copyright 2013 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
from __future__ import absolute_import

from .repository import Repository
from .team import Team
from .url_templates import URLS
from .user import User


class Organization(object):
    """A representation of an organization in a Brood server.

    """

    def __init__(self, name, url_handler):
        self.name = name
        self._url_handler = url_handler

    def __repr__(self):
        return '<{cls} organization_name={organization!r}>'.format(
            cls=type(self).__name__,
            organization=self.name,
        )

    def delete(self):
        """Delete this organization from Brood.

        """
        raise NotImplementedError('Not implemented in brood.')

    def metadata(self):
        """Get the metadata for this organization.

        """
        raise NotImplementedError('Not implemented in brood.')

    def list_repositories(self):
        """List all repositories in this organization.

        """
        path = URLS.admin.organizations.repositories.format(
            organization_name=self.name,
        )
        data = self._url_handler.get_json(path)
        return data['repositories']

    def create_repository(self, name, description):
        """Create a new repository called ``name`` inside this organization.

        Parameters
        ----------
        name : str
            The name of the repository.
        description : str
            The description of the repository.

        Returns :class:`~hatcher.core.repository.Repository`

        """
        path = URLS.admin.organizations.repositories.format(
            organization_name=self.name,
        )
        data = {
            "name": name,
            "description": description,
        }
        self._url_handler.post(path, data)
        return self.repository(name)

    def repository(self, name):
        """Get an existing repository.

        Parameters
        ----------
        name : str
            The name of the repository.

        Returns :class:`~hatcher.core.repository.Repository`

        """
        return Repository(self.name, name, url_handler=self._url_handler)

    def list_teams(self):
        """List all teams in an organization.

        """
        path = URLS.admin.organizations.teams.format(
            organization_name=self.name,
        )
        data = self._url_handler.get_json(path)
        return data['teams']

    def create_team(self, name, group_name):
        """Create a new team called ``name`` with the permissions of the group
        called ``group_name``.

        Parameters
        ----------
        name : str
            The name of the team.
        group_name : str
            The name of the group to assign to the team.

        Returns :class:`~hatcher.core.team.Team`

        """
        path = URLS.admin.organizations.teams.format(
            organization_name=self.name,
        )
        data = {
            'group': group_name,
            'name': name,
        }
        self._url_handler.post(path, data)
        return self.team(name)

    def team(self, team_name):
        """Get the team called ``team_name``.

        Parameters
        ----------
        name : str
            The name of the team.

        Returns :class:`~hatcher.core.team.Team`

        """
        return Team(self.name, team_name, url_handler=self._url_handler)

    def list_users(self):
        """List all users in the organization.

        """
        raise NotImplementedError('Not implemented in brood.')

    def create_user(self, email, teams=None):
        """Create a new user

        Parameters
        ----------
        user_email : str
            The email address of the user.

        Returns :class:`~hatcher.core.user.User`

        """
        path = URLS.admin.organizations.users.format(
            organization_name=self.name,
        )
        data = {
            'email': email,
        }
        if teams is not None:
            data['teams'] = [team.name for team in teams]
        self._url_handler.post(path, data=data)
        return self.user(email)

    def user(self, user_email):
        """Get the user with email ``user_email``.

        Parameters
        ----------
        user_email : str
            The email address of the user.

        Returns :class:`~hatcher.core.user.User`

        """
        return User(self.name, user_email, url_handler=self._url_handler)
