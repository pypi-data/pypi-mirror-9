#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright 2013 Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

import base64
import cherrypy
import datetime

from ..rest import Resource, RestException, AccessException, loadmodel
from ..describe import Description
from girder.api import access
from girder.constants import AccessType, SettingKey, TokenScope
from girder.models.token import genToken
from girder.utility import mail_utils


class User(Resource):
    """API Endpoint for users in the system."""

    def __init__(self):
        self.resourceName = 'user'

        self.route('DELETE', ('authentication',), self.logout)
        self.route('DELETE', (':id',), self.deleteUser)
        self.route('GET', (), self.find)
        self.route('GET', ('me',), self.getMe)
        self.route('GET', ('authentication',), self.login)
        self.route('GET', (':id',), self.getUser)
        self.route('POST', (), self.createUser)
        self.route('PUT', (':id',), self.updateUser)
        self.route('PUT', ('password',), self.changePassword)
        self.route('GET', ('password', 'temporary', ':id'),
                   self.checkTemporaryPassword)
        self.route('PUT', ('password', 'temporary'),
                   self.generateTemporaryPassword)
        self.route('DELETE', ('password',), self.resetPassword)

    @access.public
    def find(self, params):
        """
        Get a list of users. You can pass a "text" parameter to filter the
        users by a full text search string.

        :param [text]: Full text search.
        :param limit: The result set size limit, default=50.
        :param offset: Offset into the results, default=0.
        :param sort: The field to sort by, default=name.
        :param sortdir: 1 for ascending, -1 for descending, default=1.
        """
        limit, offset, sort = self.getPagingParameters(params, 'lastName')
        currentUser = self.getCurrentUser()

        return [self.model('user').filter(user, currentUser)
                for user in self.model('user').search(
                    text=params.get('text'), user=currentUser,
                    offset=offset, limit=limit, sort=sort)]
    find.description = (
        Description('List or search for users.')
        .responseClass('User')
        .param('text', "Pass this to perform a full text search for items.",
               required=False)
        .param('limit', "Result set size limit (default=50).", required=False,
               dataType='int')
        .param('offset', "Offset into result set (default=0).", required=False,
               dataType='int')
        .param('sort', "Field to sort the user list by (default=lastName)",
               required=False)
        .param('sortdir', "1 for ascending, -1 for descending (default=1)",
               required=False, dataType='int'))

    @access.public
    @loadmodel(map={'id': 'userToGet'}, model='user', level=AccessType.READ)
    def getUser(self, userToGet, params):
        currentUser = self.getCurrentUser()
        return self.model('user').filter(userToGet, currentUser)
    getUser.description = (
        Description('Get a user by ID.')
        .responseClass('User')
        .param('id', 'The ID of the user.', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('You do not have permission to see this user.', 403))

    @access.public
    def getMe(self, params):
        currentUser = self.getCurrentUser()
        return self.model('user').filter(currentUser, currentUser)
    getMe.description = (
        Description('Retrieve the currently logged-in user information.')
        .responseClass('User'))

    @access.public
    def login(self, params):
        """
        Login endpoint. Sends an auth cookie in the response on success.
        The caller is expected to use HTTP Basic Authentication when calling
        this endpoint.
        """
        user, token = self.getCurrentUser(returnToken=True)

        # Only create and send new cookie if user isn't already sending
        # a valid one.
        if not user:
            authHeader = cherrypy.request.headers.get('Authorization')

            if not authHeader or not authHeader[0:6] == 'Basic ':
                raise RestException('Use HTTP Basic Authentication', 401)

            try:
                credentials = base64.b64decode(authHeader[6:])
                if ':' not in credentials:
                    raise TypeError
            except Exception:
                raise RestException('Invalid HTTP Authorization header', 401)

            login, password = credentials.split(':', 1)

            login = login.lower().strip()
            loginField = 'email' if '@' in login else 'login'

            user = self.model('user').findOne({loginField: login})
            if user is None:
                raise RestException('Login failed.', code=403)

            if not self.model('password').authenticate(user, password):
                raise RestException('Login failed.', code=403)

            setattr(cherrypy.request, 'girderUser', user)
            token = self.sendAuthTokenCookie(user)

        return {
            'user': self.model('user').filter(user, user),
            'authToken': {
                'token': token['_id'],
                'expires': token['expires']
            },
            'message': 'Login succeeded.'
        }
    login.description = (
        Description('Log in to the system.')
        .notes('Pass your username and password using HTTP Basic Auth. Sends'
               ' a cookie that should be passed back in future requests.')
        .errorResponse('Missing Authorization header.', 401)
        .errorResponse('Invalid login or password.', 403))

    @access.user
    def logout(self, params):
        _, token = self.getCurrentUser(True)
        if token:
            self.model('token').remove(token)
        self.deleteAuthTokenCookie()
        return {'message': 'Logged out.'}
    logout.description = (
        Description('Log out of the system.')
        .responseClass('Token')
        .notes('Attempts to delete your authentication cookie.'))

    @access.public
    def createUser(self, params):
        self.requireParams(
            ('firstName', 'lastName', 'login', 'password', 'email'), params)

        currentUser = self.getCurrentUser()

        if currentUser is not None and currentUser['admin']:
            admin = self.boolParam('admin', params, default=False)
        else:
            admin = False
            regPolicy = self.model('setting').get(
                SettingKey.REGISTRATION_POLICY, default='open')
            if regPolicy != 'open':
                raise RestException(
                    'Registration on this instance is closed. Contact an '
                    'administrator to create an account for you.')

        user = self.model('user').createUser(
            login=params['login'], password=params['password'],
            email=params['email'], firstName=params['firstName'],
            lastName=params['lastName'], admin=admin)

        if currentUser is None:
            setattr(cherrypy.request, 'girderUser', user)
            self.sendAuthTokenCookie(user)

        return self.model('user').filter(user, user)
    createUser.description = (
        Description('Create a new user.')
        .responseClass('User')
        .param('login', "The user's requested login.")
        .param('email', "The user's email address.")
        .param('firstName', "The user's first name.")
        .param('lastName', "The user's last name.")
        .param('password', "The user's requested password")
        .param('admin', 'Whether this user should be a site administrator.',
               required=False, dataType='boolean')
        .errorResponse('A parameter was invalid, or the specified login or'
                       ' email already exists in the system.'))

    @access.user
    @loadmodel(map={'id': 'userToDelete'}, model='user', level=AccessType.ADMIN)
    def deleteUser(self, userToDelete, params):
        self.model('user').remove(userToDelete)
        return {'message': 'Deleted user %s.' % userToDelete['login']}
    deleteUser.description = (
        Description('Delete a user by ID.')
        .param('id', 'The ID of the user.', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('You do not have permission to delete this user.', 403))

    @access.user
    @loadmodel(model='user', level=AccessType.WRITE)
    def updateUser(self, user, params):
        self.requireParams(('firstName', 'lastName', 'email'), params)

        user['firstName'] = params['firstName']
        user['lastName'] = params['lastName']
        user['email'] = params['email']

        currentUser = self.getCurrentUser()

        # Only admins can change admin state
        if 'admin' in params:
            newAdminState = params['admin'] == 'true'
            if currentUser['admin']:
                user['admin'] = newAdminState
            else:
                if newAdminState != user['admin']:
                    raise AccessException('Only admins may change admin state.')

        savedUser = self.model('user').save(user)
        return self.model('user').filter(savedUser, currentUser)
    updateUser.description = (
        Description("Update a user's information.")
        .param('id', 'The ID of the user.', paramType='path')
        .param('firstName', 'First name of the user.')
        .param('lastName', 'Last name of the user.')
        .param('email', 'The email of the user.')
        .param('admin', 'Is the user a site admin (admin access required)',
               required=False, dataType='boolean')
        .errorResponse()
        .errorResponse('You do not have write access for this user.', 403)
        .errorResponse('Must be an admin to create an admin.', 403))

    @access.user
    def changePassword(self, params):
        self.requireParams(('old', 'new'), params)
        user = self.getCurrentUser()

        if not self.model('password').authenticate(user, params['old']):
            token = self.model('token').load(
                params['old'], force=True, objectId=False, exc=False)
            if (not token or not token.get('userId', None) or
                    str(token['userId']) != str(user['_id']) or
                    not self.model('token').hasScope(
                        token, TokenScope.TEMPORARY_USER_AUTH)):
                raise RestException('Old password is incorrect.', code=403)

        self.model('user').setPassword(user, params['new'])
        return {'message': 'Password changed.'}
    changePassword.description = (
        Description('Change your password.')
        .param('old', 'Your current password or a temporary access token.')
        .param('new', 'Your new password.')
        .errorResponse('You are not logged in.', 401)
        .errorResponse('Your old password is incorrect.', 403)
        .errorResponse('Your new password is invalid.'))

    @access.public
    def resetPassword(self, params):
        self.requireParams('email', params)
        email = params['email'].lower().strip()

        user = self.model('user').findOne({'email': email})
        if user is None:
            raise RestException('That email is not registered.')

        randomPass = genToken(length=12)

        html = mail_utils.renderTemplate('resetPassword.mako', {
            'password': randomPass
        })
        mail_utils.sendEmail(to=email, subject='Girder: Password reset',
                             text=html)
        self.model('user').setPassword(user, randomPass)
        return {'message': 'Sent password reset email.'}
    resetPassword.description = (
        Description('Reset a forgotten password via email.')
        .param('email', 'Your email address.')
        .errorResponse('That email does not exist in the system.'))

    @access.public
    def generateTemporaryPassword(self, params):
        self.requireParams('email', params)
        email = params['email'].lower().strip()

        users = self.model('user').find({'email': email})

        if not users.count():
            raise RestException('That email is not registered.')
        for user in users:
            token = self.model('token').createToken(None, days=1, scope=(
                TokenScope.USER_AUTH, TokenScope.TEMPORARY_USER_AUTH))
            token['userId'] = user['_id']
            self.model('token').save(token)
            base = cherrypy.request.base.rstrip('/')
            altbase = cherrypy.request.headers.get('X-Forwarded-Host', '')
            if altbase:
                base = '%s://%s' % (cherrypy.request.scheme, altbase)
            url = '%s/#useraccount/%s/token/%s' % (
                base, str(user['_id']), str(token['_id']))

            html = mail_utils.renderTemplate('temporaryAccess.mako', {
                'url': url,
                'token': str(token['_id'])
            })
            mail_utils.sendEmail(to=email, subject='Girder: Temporary Access',
                                 text=html)
        return {'message': 'Sent temporary access email.'}
    generateTemporaryPassword.description = (
        Description('Create a temporary access token for a user.  The user\'s '
                    'password is not changed.')
        .param('email', 'Your email address.')
        .errorResponse('That email does not exist in the system.'))

    @access.public
    def checkTemporaryPassword(self, id, params):
        self.requireParams('token', params)
        token = self.model('token').load(
            params['token'], force=True, objectId=False, exc=False)
        if (not token or not token.get('userId', None) or
                str(token['userId']) != id or
                not self.model('token').hasScope(
                    token, TokenScope.TEMPORARY_USER_AUTH)):
            raise RestException('The token does not grant temporary access to '
                                'the specified user.', code=403)
        delta = (token['expires'] - datetime.datetime.utcnow()).total_seconds()
        if delta <= 0:
            raise RestException('The token does not grant temporary access to '
                                'the specified user.', code=403)
        # We have verified that this token allows access to this user, so force
        # loading the user.
        user = self.model('user').load(id, force=True)
        # Send an auth cookie with our token
        cookie = cherrypy.response.cookie
        cookie['girderToken'] = str(token['_id'])
        cookie['girderToken']['path'] = '/'
        cookie['girderToken']['expires'] = int(delta)

        return {
            'user': self.model('user').filter(user, user),
            'authToken': {
                'token': token['_id'],
                'expires': token['expires'],
                'temporary': True
            },
            'message': 'Temporary access token is valid.'
        }
    checkTemporaryPassword.description = (
        Description('Check if a specified token is a temporary access token '
                    'for the specified user.  If the token is valid, returns '
                    'information on the token and user.')
        .param('id', 'The user ID to check.', paramType='path')
        .param('token', 'The token to check.')
        .errorResponse('The token does not grant temporary access to the '
                       'specified user.', 403))
