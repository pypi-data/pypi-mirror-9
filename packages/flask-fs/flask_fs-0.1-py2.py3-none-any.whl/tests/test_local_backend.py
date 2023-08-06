# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import shutil
import tempfile

from os.path import join, exists

from . import TestCase

from flask.ext.fs.exceptions import FileExists
from flask.ext.fs.backends.local import LocalBackend
from flask.ext.fs.storage import Config


class LocalBackendTest(TestCase):
    def setUp(self):
        super(LocalBackendTest, self).setUp()
        self.test_dir = tempfile.mkdtemp()
        self.config = Config({
            'root': self.test_dir,
        })
        self.backend = LocalBackend('test', self.config)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_root(self):
        self.assertEqual(self.backend.root, self.test_dir)

    def test_default_root(self):
        self.app.config['FS_ROOT'] = self.test_dir
        root = join(self.test_dir, 'default')
        backend = LocalBackend('default', Config({}))
        with self.app.app_context():
            self.assertEqual(backend.root, root)

    def test_exists(self):
        with open(join(self.test_dir, 'file.test'), 'w') as f:
            f.write('test')

        self.assertTrue(self.backend.exists('file.test'))
        self.assertFalse(self.backend.exists('other.test'))

    def test_open(self):
        content = 'test'
        with open(join(self.test_dir, 'file.test'), 'w') as f:
            f.write(content)

        with self.backend.open('file.test') as f:
            self.assertEqual(f.read(), content)

    def test_read(self):
        content = 'test'
        with open(join(self.test_dir, 'file.test'), 'w') as f:
            f.write(content)

        self.assertEqual(self.backend.read('file.test'), content)

    def test_write(self):
        content = 'test'
        self.backend.write('test.txt', content)

        with open(join(self.test_dir, 'test.txt'), 'r') as f:
            self.assertEqual(f.read(), content)

    def test_delete(self):
        with open(join(self.test_dir, 'file.test'), 'w') as f:
            f.write('test')

        self.backend.delete('file.test')

        self.assertFalse(exists(join(self.test_dir, 'file.test')))

    def test_save_content(self):
        content = 'test'
        storage = self.filestorage('test.txt', content)
        self.backend.save(storage, 'test.txt')

        with open(join(self.test_dir, 'test.txt'), 'r') as f:
            self.assertEqual(f.read(), content)

    def test_save_from_file(self):
        f = self.app.open_resource('flask.png')
        self.backend.save(f, 'test.png')

        f.seek(0)
        filename = join(self.test_dir, 'test.png')
        with open(filename, 'r') as out:
            self.assertEqual(f.read(), out.read())

    def test_save_with_filename(self):
        content = 'test'
        storage = self.filestorage('test.txt', content)
        self.backend.save(storage, 'somewhere/test.test')

        with open(join(self.test_dir, 'somewhere/test.test'), 'r') as f:
            self.assertEqual(f.read(), content)

    def test_save_deny_overwrite(self):
        filename = 'file.test'
        with open(join(self.test_dir, filename), 'w') as f:
            f.write('initial')

        content = 'test'
        storage = self.filestorage('whatever', content)
        with self.assertRaises(FileExists):
            self.backend.save(storage, filename)

    def test_save_allow_overwrite(self):
        filename = 'file.test'
        with open(join(self.test_dir, filename), 'w') as f:
            f.write('initial')

        content = 'test'
        storage = self.filestorage('whatever', content)
        self.backend.save(storage, filename, overwrite=True)

        with open(join(self.test_dir, 'file.test'), 'r') as f:
            self.assertEqual(f.read(), content)
