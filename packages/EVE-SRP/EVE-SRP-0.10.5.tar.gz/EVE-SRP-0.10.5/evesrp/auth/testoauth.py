from __future__ import absolute_import
from flask import request, abort, current_app
import six
from sqlalchemy.orm.exc import NoResultFound

from .oauth import OAuthMethod, OAuthUser
from .. import db
from .models import Group, Pilot


class TestOAuth(OAuthMethod):

    def __init__(self, devtest=False, **kwargs):
        """:py:class:`~.AuthMethod` using TEST Auth's OAuth-based API for
        authentication and authorization.

        :param list admins: Two types of values are accepted as values in this
            list, either a string specifying a user's primary character's name,
            or their Auth ID as an integer.
        :param bool devtest: Testing parameter that changes the default domain
            for URLs from 'https://auth.pleaseignore.com' to
            'https://auth.devtest.pleaseignore.com`. Default: ``False``.
        :param str authorize_url: The URL to request OAuth authorization
            tokens. Default:
            ``'https://auth.pleaseignore.com/oauth2/authorize'``.
        :param str access_token_url: The URL for OAuth token exchange. Default:
            ``'https://auth.pleaseignore.com/oauth2/access_token'``.
        :param str base_str: The base URL for API requests. Default:
            ``'https://auth.pleaseignore.com/api/v3/'``.
        :param dict request_token_params: Additional parameters to include with
            the authorization token request. Default: ``{'scope':
            'private-read'}``.
        :param str access_token_method: HTTP Method to use for exchanging
            authorization tokens for access tokens. Default: ``'POST'``.
        :param str name: The name for this authentication method. Default:
            ``'Test OAuth'``.
        """
        if not devtest:
            domain = 'https://auth.pleaseignore.com'
        else:
            domain = 'https://auth.devtest.pleaseignore.com'
        kwargs.setdefault('authorize_url',
                domain + '/oauth2/authorize')
        kwargs.setdefault('access_token_url',
                domain + '/oauth2/access_token')
        kwargs.setdefault('base_url',
                domain + '/api/v3/')
        kwargs.setdefault('request_token_params', {'scope': 'private-read'})
        kwargs.setdefault('access_token_method', 'POST')
        kwargs.setdefault('app_key', 'TEST_OAUTH')
        kwargs.setdefault('name', u'Test OAuth')
        super(TestOAuth, self).__init__(**kwargs)

    def _get_user_data(self, token):
        if not hasattr(request, '_auth_user_data'):
            resp = self.oauth.get('profile', token=token)
            try:
                current_app.logger.debug(u"Test OAuth API response: {}".format(
                        resp.data))
                request._auth_user_data = resp.data[u'objects'][0]
            except TypeError:
                abort(500, u"Error in receiving OAuth response: {}".format(
                        resp.data))
        return request._auth_user_data

    def get_user(self, token):
        data = self._get_user_data(token)
        char_data = self.oauth.get('evecharacter', token=token).data
        primary_character = char_data[u'objects'][0][u'name']
        user_id = data[u'id']
        try:
            user = TestOAuthUser.query.filter_by(auth_id=data[u'id'],
                    authmethod=self.name).one()
            # The primary character can change
            user.name = primary_character
        except NoResultFound:
            user = TestOAuthUser(primary_character, user_id, self.name,
                    token=token['access_token'])
            db.session.add(user)
            db.session.commit()
        return user

    def is_admin(self, user):
        data = self._get_user_data(user.token)
        return super(TestOAuth, self).is_admin(user) or \
                user.auth_id in self.admins or \
                data[u'is_staff'] or \
                data[u'is_superuser']

    def get_pilots(self, token):
        data = self._get_user_data(token)
        # The Auth API will duplicate characters when there's more than one API
        # key for them.
        pilots = {}
        for character in data[u'characters']:
            pilot = Pilot.query.get(int(character[u'id']))
            if pilot is None:
                pilot = Pilot(None, character[u'name'], character[u'id'])
            pilots[character[u'id']] = pilot
        pilots = list(pilots.values())
        return pilots

    def get_groups(self, token):
        data = self._get_user_data(token)
        groups = []
        for group_info in data[u'groups']:
            group_name = group_info[u'name']
            group_id = group_info[u'id']
            try:
                group = TestOAuthGroup.query.filter_by(auth_id=group_id,
                        authmethod=self.name).one()
            except NoResultFound:
                group = TestOAuthGroup(group_name, group_id, self.name)
                db.session.add(group)
            if group.name != group_name:
                group.name = group_name
            groups.append(group)
        db.session.commit()
        return groups


class TestOAuthUser(OAuthUser):

    id = db.Column(db.Integer, db.ForeignKey(OAuthUser.id), primary_key=True)

    auth_id = db.Column(db.Integer, nullable=False, unique=True, index=True)

    def __init__(self, username, auth_id, authmethod, groups=None, **kwargs):
        self.auth_id = auth_id
        super(TestOAuthUser, self).__init__(username, authmethod, **kwargs)


class TestOAuthGroup(Group):

    id = db.Column(db.Integer, db.ForeignKey(Group.id), primary_key=True)

    auth_id = db.Column(db.Integer, nullable=False, unique=True, index=True)

    def __init__(self, name, auth_id, authmethod, **kwargs):
        self.auth_id = auth_id
        super(TestOAuthGroup, self).__init__(name, authmethod, **kwargs)
