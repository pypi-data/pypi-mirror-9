# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
import shutil
import tempfile

from os.path import join

from flask import url_for

from . import TestCase

from flask.ext import fs


class MockBackend(fs.BaseBackend):
    pass


MOCK_BACKEND = '.'.join((__name__, MockBackend.__name__))


def mock_backend(func):
    return mock.patch(MOCK_BACKEND)(func)


class ViewsTestCase(TestCase):
    def setUp(self):
        super(ViewsTestCase, self).setUp()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the directory after the test
        shutil.rmtree(self.test_dir)

    def configure(self, *storages, **configs):
        self.app.config['FS_BACKEND'] = configs.pop('FS_BACKEND', MOCK_BACKEND)
        super(ViewsTestCase, self).configure(*storages, **configs)

    def test_url(self):
        storage = fs.Storage('test')

        self.configure(storage, SERVER_NAME='somewhere')

        with self.app.app_context():
            expected_url = url_for('fs.get_file', fs=storage.name, filename='test.txt')
            self.assertEqual(storage.url('test.txt'), expected_url)

    @mock_backend
    def test_get_file(self, mock_backend):
        storage = fs.Storage('test')
        backend = mock_backend.return_value
        backend.root = self.test_dir
        filename = 'test.txt'

        with open(join(self.test_dir, 'test.txt'), 'wb') as out:
            out.write('content'.encode('utf8'))

        self.configure(storage, SERVER_NAME='somewhere')

        with self.app.app_context():
            file_url = url_for('fs.get_file', fs='test', filename=filename)

        response = self.client.get(file_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, 'content'.encode('utf8'))

    @mock_backend
    def test_get_file_unsupported(self, mock_backend):
        storage = fs.Storage('test')
        backend = mock_backend.return_value
        backend.root = None

        self.configure(storage, SERVER_NAME='somewhere')

        with self.app.app_context():
            file_url = url_for('fs.get_file', fs='test', filename='test.txt')

        response = self.client.get(file_url)
        self.assertEqual(response.status_code, 404)

    def test_get_file_no_storage(self):
        self.configure(SERVER_NAME='somewhere')

        with self.app.app_context():
            file_url = url_for('fs.get_file', fs='fake', filename='test.txt')

        response = self.client.get(file_url)
        self.assertEqual(response.status_code, 404)
