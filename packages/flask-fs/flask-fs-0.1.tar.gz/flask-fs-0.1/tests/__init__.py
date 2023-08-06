# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import unittest
import six

from flask import Flask
from werkzeug.datastructures import FileStorage

BIN_FILE = os.path.join(os.path.dirname(__file__), 'flask.png')


class TestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def configure(self, *storages, **configs):
        from flask.ext import fs
        for key, value in configs.items():
            self.app.config[key] = value
        fs.init_app(self.app, *storages)

    def filestorage(self, filename, content):
        if isinstance(content, six.binary_type):
            data = six.BytesIO(content)
        elif isinstance(content, six.string_types):
            data = six.StringIO(content)
        else:
            data = content
        return FileStorage(data, filename)
