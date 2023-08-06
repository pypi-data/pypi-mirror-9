# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import join

__version__ = '0.1'
__description__ = 'Simple and easy file storages for Flask'

try:
    from flask import current_app

    from .backends import BaseBackend, DEFAULT_BACKEND, BUILTIN_BACKENDS
    from .exceptions import *
    from .files import *
    from .storage import Storage

except ImportError as e:
    print(e)


def by_name(name):
    '''Get a storage by its name'''
    return current_app.extensions['fs'].get(name)


def init_app(app, *storages):
    '''
    Initialize Storages configuration
    Register blueprint if necessary.

    :param app: The `~flask.Flask` instance to get the configuration from.
    :param storages: A  `Storage` instance list to register and configure.
    '''

    # Set default configuration
    app.config.setdefault('FS_SERVE', app.config.get('DEBUG', False))
    app.config.setdefault('FS_ROOT', join(app.instance_path, 'fs'))
    app.config.setdefault('FS_PREFIX', None)
    app.config.setdefault('FS_URL', None)
    app.config.setdefault('FS_BACKEND', 'local')

    state = app.extensions['fs'] = app.extensions.get('fs', {})
    for storage in storages:
        storage.configure(app)
        state[storage.name] = storage

    from .views import bp
    app.register_blueprint(bp, url_prefix=app.config['FS_PREFIX'])
