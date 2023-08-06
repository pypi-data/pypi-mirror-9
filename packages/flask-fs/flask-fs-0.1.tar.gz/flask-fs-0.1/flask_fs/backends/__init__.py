# -*- coding: utf-8 -*-
from __future__ import unicode_literals

__all__ = [i.encode('ascii') for i in ('BaseBackend', 'DEFAULT_BACKEND', 'BUILTIN_BACKENDS')]


BUILTIN_BACKENDS = {
    'local': 'flask.ext.fs.backends.local.LocalBackend',
    's3': 'flask.ext.fs.backends.s3.S3Backend',
    'swift': 'flask.ext.fs.backends.swift.SwiftBackend',
    'grids': 'flask.ext.fs.backends.gridfs.GridFSBackend',
}

DEFAULT_BACKEND = 'local'


class BaseBackend(object):
    '''
    Abstract class to implement backend.
    '''
    root = None

    def __init__(self, name, config):
        self.name = name
        self.config = config

    def exists(self, filename):
        '''Test wether a file exists or not given its filename in the storage'''
        raise NotImplementedError('Existance checking is not implemented')

    def read(self, filename):
        '''Read a file content given its filename in the storage'''
        raise NotImplementedError('Read operation is not implemented')

    def write(self, filename, content):
        '''Write content into a file given its filename in the storage'''
        raise NotImplementedError('Write operation is not implemented')

    def delete(self, filename):
        '''Delete a file given its filename in the storage'''
        raise NotImplementedError('Delete operation is not implemented')

    def save(self, storage, filename, overwrite=False):
        '''
        Save a `werkzeug.FileStorage` with the specified filename.

        :param storage: The storage to be saved.
        :param filename: The destination of the storage.
        :param overwrite: Whethe overwriting is allowed or not.

        If `overwrite` is `False` and the file exists,
        a `FileExists` exception will be raised.
        '''
        raise NotImplementedError('Save operation is not implemented')
