# -*- coding: utf-8 -*-

#    Copyright (C) 2013 Rackspace Hosting All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import contextlib

from taskflow import exceptions as exc
from taskflow.persistence import backends
from taskflow.persistence.backends import impl_memory
from taskflow import test
from taskflow.tests.unit.persistence import base


class MemoryPersistenceTest(test.TestCase, base.PersistenceTestMixin):
    def setUp(self):
        super(MemoryPersistenceTest, self).setUp()
        self._backend = impl_memory.MemoryBackend({})

    def _get_connection(self):
        return self._backend.get_connection()

    def tearDown(self):
        conn = self._get_connection()
        conn.clear_all()
        self._backend = None
        super(MemoryPersistenceTest, self).tearDown()

    def test_memory_backend_entry_point(self):
        conf = {'connection': 'memory:'}
        with contextlib.closing(backends.fetch(conf)) as be:
            self.assertIsInstance(be, impl_memory.MemoryBackend)

    def test_memory_backend_fetch_by_name(self):
        conf = {'connection': 'memory'}  # note no colon
        with contextlib.closing(backends.fetch(conf)) as be:
            self.assertIsInstance(be, impl_memory.MemoryBackend)


class MemoryFilesystemTest(test.TestCase):

    @staticmethod
    def _get_item_path(fs, path):
        # TODO(harlowja): is there a better way to do this??
        return fs[path]

    @staticmethod
    def _del_item_path(fs, path):
        # TODO(harlowja): is there a better way to do this??
        del fs[path]

    def test_set_get_ls(self):
        fs = impl_memory.FakeFilesystem()
        fs['/d'] = 'd'
        fs['/c'] = 'c'
        fs['/d/b'] = 'db'
        self.assertEqual(2, len(fs.ls('/')))
        self.assertEqual(1, len(fs.ls('/d')))
        self.assertEqual('d', fs['/d'])
        self.assertEqual('c', fs['/c'])
        self.assertEqual('db', fs['/d/b'])

    def test_ensure_path(self):
        fs = impl_memory.FakeFilesystem()
        pieces = ['a', 'b', 'c']
        path = "/" + "/".join(pieces)
        fs.ensure_path(path)
        path = fs.root_path
        for i, p in enumerate(pieces):
            if i == 0:
                path += p
            else:
                path += "/" + p
            self.assertIsNone(fs[path])

    def test_not_found(self):
        fs = impl_memory.FakeFilesystem()
        self.assertRaises(exc.NotFound, self._get_item_path, fs, '/c')

    def test_del_root_not_allowed(self):
        fs = impl_memory.FakeFilesystem()
        self.assertRaises(ValueError, self._del_item_path, fs, '/')

    def test_link_loop_raises(self):
        fs = impl_memory.FakeFilesystem()
        fs['/b'] = 'c'
        fs.symlink('/b', '/b')
        self.assertRaises(ValueError, self._get_item_path, fs, '/b')

    def test_ensure_linked_delete(self):
        fs = impl_memory.FakeFilesystem()
        fs['/b'] = 'd'
        fs.symlink('/b', '/c')
        self.assertEqual('d', fs['/b'])
        self.assertEqual('d', fs['/c'])
        del fs['/b']
        self.assertRaises(exc.NotFound, self._get_item_path, fs, '/c')
        self.assertRaises(exc.NotFound, self._get_item_path, fs, '/b')
