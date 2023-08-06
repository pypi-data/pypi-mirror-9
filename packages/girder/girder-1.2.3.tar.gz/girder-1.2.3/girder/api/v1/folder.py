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

import cherrypy
import json

from ..describe import Description
from ..rest import Resource, RestException, loadmodel
from ...constants import AccessType
from girder.utility import ziputil
from girder.utility.progress import ProgressContext
from girder.api import access


class Folder(Resource):
    """API Endpoint for folders."""

    def __init__(self):
        self.resourceName = 'folder'
        self.route('DELETE', (':id',), self.deleteFolder)
        self.route('GET', (), self.find)
        self.route('GET', (':id',), self.getFolder)
        self.route('GET', (':id', 'access'), self.getFolderAccess)
        self.route('GET', (':id', 'download'), self.downloadFolder)
        self.route('POST', (), self.createFolder)
        self.route('PUT', (':id',), self.updateFolder)
        self.route('PUT', (':id', 'access'), self.updateFolderAccess)
        self.route('POST', (':id', 'copy'), self.copyFolder)
        self.route('PUT', (':id', 'metadata'), self.setMetadata)

    @access.public
    def find(self, params):
        """
        Get a list of folders with given search parameters. Currently accepted
        search modes are:

        1. Searching by parentId and parentType.
        2. Searching with full text search.

        To search with full text search, pass the "text" parameter. To search
        by parent, (i.e. list child folders) pass parentId and parentType,
        which must be one of ('folder' | 'collection' | 'user'). You can also
        pass limit, offset, sort, and sortdir parameters.

        :param limit: The result set size limit, default=50.
        :param offset: Offset into the results, default=0.
        :param sort: The field to sort by, default=lowerName.
        :param sortdir: 1 for ascending, -1 for descending, default=1.
        """
        limit, offset, sort = self.getPagingParameters(params, 'lowerName')
        user = self.getCurrentUser()

        if 'parentId' in params and 'parentType' in params:
            parentType = params['parentType'].lower()
            if parentType not in ('collection', 'folder', 'user'):
                raise RestException('The parentType must be user, collection,'
                                    ' or folder.')

            parent = self.model(parentType).load(
                id=params['parentId'], user=user, level=AccessType.READ,
                exc=True)

            filters = {}
            if 'text' in params:
                filters['$text'] = {
                    '$search': params['text']
                }

            return [self.model('folder').filter(folder, user) for folder in
                    self.model('folder').childFolders(
                        parentType=parentType, parent=parent, user=user,
                        offset=offset, limit=limit, sort=sort, filters=filters)]
        elif 'text' in params:
            return [self.model('folder').filter(folder, user) for folder in
                    self.model('folder').textSearch(
                        params['text'], user=user, limit=limit, offset=offset,
                        sort=sort)]
        else:
            raise RestException('Invalid search mode.')
    find.description = (
        Description('Search for folders by certain properties.')
        .responseClass('Folder')
        .param('parentType', "Type of the folder's parent", required=False,
               enum=['folder', 'user', 'collection'])
        .param('parentId', "The ID of the folder's parent.", required=False)
        .param('text', 'Pass to perform a text search.', required=False)
        .param('limit', "Result set size limit (default=50).", required=False,
               dataType='int')
        .param('offset', "Offset into result set (default=0).", required=False,
               dataType='int')
        .param('sort', "Field to sort the folder list by (default=name)",
               required=False)
        .param('sortdir', "1 for ascending, -1 for descending (default=1)",
               required=False, dataType='int')
        .errorResponse()
        .errorResponse('Read access was denied on the parent resource.', 403))

    @access.public
    @loadmodel(model='folder', level=AccessType.READ)
    def downloadFolder(self, folder, params):
        """
        Returns a generator function that will be used to stream out a zip
        file containing this folder's contents, filtered by permissions.
        """
        cherrypy.response.headers['Content-Type'] = 'application/zip'
        cherrypy.response.headers['Content-Disposition'] = \
            u'attachment; filename="{}{}"'.format(folder['name'], '.zip')

        user = self.getCurrentUser()

        def stream():
            zip = ziputil.ZipGenerator(folder['name'])
            for (path, file) in self.model('folder').fileList(
                    folder, user=user, subpath=False):
                for data in zip.addFile(file, path):
                    yield data
            yield zip.footer()
        return stream
    downloadFolder.cookieAuth = True
    downloadFolder.description = (
        Description('Download an entire folder as a zip archive.')
        .param('id', 'The ID of the folder.', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Read access was denied for the folder.', 403))

    @access.user
    @loadmodel(model='folder', level=AccessType.WRITE)
    def updateFolder(self, folder, params):
        user = self.getCurrentUser()
        folder['name'] = params.get('name', folder['name']).strip()
        folder['description'] = params.get(
            'description', folder['description']).strip()

        folder = self.model('folder').updateFolder(folder)

        if 'parentType' in params and 'parentId' in params:
            parentType = params['parentType'].lower()
            if parentType not in ('user', 'collection', 'folder'):
                raise RestException('Invalid parentType.')

            parent = self.model(parentType).load(
                params['parentId'], level=AccessType.WRITE, user=user, exc=True)
            if (parentType, parent['_id']) !=\
               (folder['parentCollection'], folder['parentId']):
                folder = self.model('folder').move(folder, parent, parentType)

        return self.model('folder').filter(folder, user)
    updateFolder.description = (
        Description('Update a folder or move it into a new parent.')
        .responseClass('Folder')
        .param('id', 'The ID of the folder.', paramType='path')
        .param('name', 'Name of the folder.', required=False)
        .param('description', 'Description for the folder.', required=False)
        .param('parentType', "Type of the folder's parent", required=False,
               enum=['folder', 'user', 'collection'])
        .param('parentId', 'Parent ID for the new parent of this folder.',
               required=False)
        .errorResponse('ID was invalid.')
        .errorResponse('Write access was denied for the folder or its new '
                       'parent object.', 403))

    @access.user
    @loadmodel(model='folder', level=AccessType.ADMIN)
    def updateFolderAccess(self, folder, params):
        self.requireParams('access', params)

        public = self.boolParam('public', params, default=False)
        self.model('folder').setPublic(folder, public)

        try:
            access = json.loads(params['access'])
            return self.model('folder').setAccessList(
                folder, access, save=True)
        except ValueError:
            raise RestException('The access parameter must be JSON.')
    updateFolderAccess.description = (
        Description('Update the access control list for a folder.')
        .param('id', 'The ID of the folder.', paramType='path')
        .param('access', 'The JSON-encoded access control list.')
        .param('public', "Whether the folder should be publicly visible.",
               dataType='boolean')
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the folder.', 403))

    @access.user
    def createFolder(self, params):
        """
        Create a new folder.

        :param parentId: The _id of the parent folder.
        :type parentId: str
        :param parentType: The type of the parent of this folder.
        :type parentType: str - 'user', 'collection', or 'folder'
        :param name: The name of the folder to create.
        :param description: Folder description.
        :param public: Public read access flag.
        :type public: bool
        """
        self.requireParams(('name', 'parentId'), params)

        user = self.getCurrentUser()
        parentType = params.get('parentType', 'folder').lower()
        name = params['name'].strip()
        description = params.get('description', '').strip()
        public = self.boolParam('public', params, default=None)

        if parentType not in ('folder', 'user', 'collection'):
            raise RestException('Set parentType to collection, folder, '
                                'or user.')

        model = self.model(parentType)

        parent = model.load(id=params['parentId'], user=user,
                            level=AccessType.WRITE, exc=True)

        folder = self.model('folder').createFolder(
            parent=parent, name=name, parentType=parentType, creator=user,
            description=description, public=public)

        if parentType in ('user', 'collection'):
            folder = self.model('folder').setUserAccess(
                folder, user=user, level=AccessType.ADMIN, save=True)

        return self.model('folder').filter(folder, user)
    createFolder.description = (
        Description('Create a new folder.')
        .responseClass('Folder')
        .param('parentType', "Type of the folder's parent", required=False,
               enum=['folder', 'user', 'collection'])
        .param('parentId', "The ID of the folder's parent.")
        .param('name', "Name of the folder.")
        .param('description', "Description for the folder.", required=False)
        .param('public', """Whether the folder should be publicly visible. By
               default, inherits the value from parent folder, or in the
               case of user or collection parentType, defaults to False.""",
               required=False, dataType='boolean')
        .errorResponse()
        .errorResponse('Write access was denied on the parent', 403))

    @access.public
    @loadmodel(model='folder', level=AccessType.READ)
    def getFolder(self, folder, params):
        """Get a folder by ID."""
        return self.model('folder').filter(folder, self.getCurrentUser())
    getFolder.description = (
        Description('Get a folder by ID.')
        .responseClass('Folder')
        .param('id', 'The ID of the folder.', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Read access was denied for the folder.', 403))

    @access.user
    @loadmodel(model='folder', level=AccessType.ADMIN)
    def getFolderAccess(self, folder, params):
        """
        Get an access list for a folder.
        """
        return self.model('folder').getFullAccessList(folder)
    getFolderAccess.description = (
        Description('Get the access control list for a folder.')
        .responseClass('Folder')
        .param('id', 'The ID of the folder.', paramType='path')
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the folder.', 403))

    @access.user
    @loadmodel(model='folder', level=AccessType.ADMIN)
    def deleteFolder(self, folder, params):
        progress = self.boolParam('progress', params, default=False)
        with ProgressContext(progress, user=self.getCurrentUser(),
                             title=u'Deleting folder {}'.format(folder['name']),
                             message='Calculating folder size...') as ctx:
            # Don't do the subtree count if we weren't asked for progress
            if progress:
                ctx.update(total=self.model('folder').subtreeCount(folder))
            self.model('folder').remove(folder, progress=ctx)
        return {'message': u'Deleted folder {}.'.format(folder['name'])}
    deleteFolder.description = (
        Description('Delete a folder by ID.')
        .param('id', 'The ID of the folder.', paramType='path')
        .param('progress', 'Whether to record progress on this task. Default '
               'is false.', required=False, dataType='boolean')
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the folder.', 403))

    @access.user
    @loadmodel(model='folder', level=AccessType.WRITE)
    def setMetadata(self, folder, params):
        metadata = self.getBodyJson()

        # Make sure we let user know if we can't accept a metadata key
        for k in metadata:
            if '.' in k or k[0] == '$':
                raise RestException(u'The key name {} must not contain a '
                                    'period or begin with a dollar sign.'
                                    .format(k))

        return self.model('folder').setMetadata(folder, metadata)
    setMetadata.description = (
        Description('Set metadata fields on an folder.')
        .responseClass('Folder')
        .notes('Set metadata fields to null in order to delete them.')
        .param('id', 'The ID of the folder.', paramType='path')
        .param('body', 'A JSON object containing the metadata keys to add',
               paramType='body')
        .errorResponse('ID was invalid.')
        .errorResponse('Invalid JSON passed in request body.')
        .errorResponse('Metadata key name was invalid.')
        .errorResponse('Write access was denied for the folder.', 403))

    @access.user
    @loadmodel(model='folder', level=AccessType.READ)
    def copyFolder(self, folder, params):
        """
        Copy an existing folder to a new folder.
        """
        user = self.getCurrentUser()
        parentType = params.get('parentType', folder['parentCollection'])
        if 'parentId' in params:
            parentId = params.get('parentId', folder['parentId'])
            parent = self.model(parentType).load(
                id=parentId, user=user, level=AccessType.WRITE, exc=True)
        else:
            parent = None
        name = params.get('name', None)
        description = params.get('description', None)
        public = params.get('public', None)
        progress = self.boolParam('progress', params, default=False)
        with ProgressContext(progress, user=self.getCurrentUser(),
                             title=u'Copying folder {}'.format(folder['name']),
                             message='Calculating folder size...') as ctx:
            # Don't do the subtree count if we weren't asked for progress
            if progress:
                ctx.update(total=self.model('folder').subtreeCount(folder))
            newFolder = self.model('folder').copyFolder(
                folder, creator=user, name=name, parentType=parentType,
                parent=parent, description=description, public=public,
                progress=ctx)
        return newFolder
    copyFolder.description = (
        Description('Copy a folder.')
        .responseClass('Folder')
        .param('id', 'The ID of the original folder.', paramType='path')
        .param('parentType', "Type of the new folder's parent", required=False,
               enum=['folder', 'user', 'collection'])
        .param('parentId', 'The ID of the parent docuemnt.', required=False)
        .param('name', 'Name for the new folder.', required=False)
        .param('description', "Description for the new folder.", required=False)
        .param('public', """Whether the folder should be publicly visible.  By
               default, inherits the value from parent folder, or in the case
               of user or collection parentType, defaults to False.  If
               'original', use the value of the original folder.""",
               required=False, enum=[True, False, 'original'])
        .param('progress', 'Whether to record progress on this task. Default '
               'is false.', required=False, dataType='boolean')
        .errorResponse()
        .errorResponse('ID was invalid.')
        .errorResponse('Read access was denied on the original folder.', 403)
        .errorResponse('Write access was denied on the parent.', 403))
