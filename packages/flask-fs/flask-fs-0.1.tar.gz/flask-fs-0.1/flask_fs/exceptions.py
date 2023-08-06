# -*- coding: utf-8 -*-
from __future__ import unicode_literals


__all__ = (
    'FSException',
    'FileExists',
    'FileNotFound',
    'UnauthorizedFileType',
    'UploadNotAllowed',
    'OperationNotSupported',
)


class FSException(Exception):
    '''Base class for all Flask-FS Exceptions'''
    pass


class UnauthorizedFileType(FSException):
    '''This exception is raised when trying to upload an unauthorized file type.'''
    pass


class UploadNotAllowed(FSException):
    '''Raised when trying to upload into storage where upload is not allowed.'''
    pass


class FileExists(FSException):
    '''Raised when trying to overwrite an existing file'''
    pass


class FileNotFound(FSException):
    '''Raised when trying to access a non existant file'''
    pass


class OperationNotSupported(FSException):
    '''Raised when trying to perform an operation not supported by the current backend'''
    pass
