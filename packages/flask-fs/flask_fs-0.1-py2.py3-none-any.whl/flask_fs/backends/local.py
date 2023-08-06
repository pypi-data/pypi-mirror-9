# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os

from shutil import copyfileobj

from flask import current_app
from werkzeug import cached_property
from werkzeug.datastructures import FileStorage

from ..exceptions import FileExists

from . import BaseBackend

log = logging.getLogger(__name__)


class LocalBackend(BaseBackend):
    @cached_property
    def root(self):
        return self.config.get('root') or os.path.join(current_app.config.get('FS_ROOT'), self.name)

    def exists(self, filename):
        dest = os.path.join(self.root, filename)
        return os.path.exists(dest)

    def open(self, filename):
        dest = os.path.join(self.root, filename)
        return open(dest)

    def read(self, filename):
        dest = os.path.join(self.root, filename)
        with open(dest) as f:
            return f.read()

    def write(self, filename, content):
        dest = os.path.join(self.root, filename)
        dirname = os.path.dirname(dest)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(dest, 'wb') as f:
            return f.write(content.encode('utf8') if hasattr(content, 'encode') else content)

    def delete(self, filename):
        dest = os.path.join(self.root, filename)
        return os.remove(dest)

    def save(self, file_or_wfs, filename, overwrite=False):
        '''
        Save a file-like object or a `werkzeug.FileStorage` with the specified filename.

        :param storage: The file or the storage to be saved.
        :param filename: The destination in the storage.
        :param overwrite: if False and file exists in storage, raise `FileExists`
        '''
        dest = os.path.join(self.root, filename)

        folder = os.path.dirname(dest)
        if not os.path.exists(folder):
            os.makedirs(folder)

        if not overwrite and os.path.exists(dest):
            raise FileExists('File exists: ' + dest)

        if isinstance(file_or_wfs, FileStorage):
            file_or_wfs.save(dest)
        else:
            with open(dest, 'wb') as out:
                copyfileobj(file_or_wfs, out)
        return filename
