# -*- coding: utf-8 -*-

#    Copyright (C) 2012 Yahoo! Inc. All Rights Reserved.
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
import errno
import os
import shutil

from oslo_serialization import jsonutils

from taskflow import exceptions as exc
from taskflow.persistence import path_based
from taskflow.utils import lock_utils
from taskflow.utils import misc


@contextlib.contextmanager
def _storagefailure_wrapper():
    try:
        yield
    except exc.TaskFlowException:
        raise
    except Exception as e:
        if isinstance(e, (IOError, OSError)) and e.errno == errno.ENOENT:
            raise exc.NotFound('Item not found: %s' % e.filename, e)
        raise exc.StorageFailure("Storage backend internal error", e)


class DirBackend(path_based.PathBasedBackend):
    """A directory and file based backend.

    This backend does *not* provide true transactional semantics. It does
    guarantee that there will be no interprocess race conditions when
    writing and reading by using a consistent hierarchy of file based locks.

    Example configuration::

        conf = {
            "path": "/tmp/taskflow",
        }
    """
    def __init__(self, conf):
        super(DirBackend, self).__init__(conf)
        self.file_cache = {}
        self.encoding = self._conf.get('encoding', 'utf-8')
        if not self._path:
            raise ValueError("Empty path is disallowed")
        self._path = os.path.abspath(self._path)
        self.lock = lock_utils.ReaderWriterLock()

    def get_connection(self):
        return Connection(self)

    def close(self):
        pass


class Connection(path_based.PathBasedConnection):
    def _read_from(self, filename):
        # This is very similar to the oslo-incubator fileutils module, but
        # tweaked to not depend on a global cache, as well as tweaked to not
        # pull-in the oslo logging module (which is a huge pile of code).
        mtime = os.path.getmtime(filename)
        cache_info = self.backend.file_cache.setdefault(filename, {})
        if not cache_info or mtime > cache_info.get('mtime', 0):
            with open(filename, 'rb') as fp:
                cache_info['data'] = misc.binary_decode(
                    fp.read(), encoding=self.backend.encoding)
                cache_info['mtime'] = mtime
        return cache_info['data']

    def _write_to(self, filename, contents):
        contents = misc.binary_encode(contents,
                                      encoding=self.backend.encoding)
        with open(filename, 'wb') as fp:
            fp.write(contents)
        self.backend.file_cache.pop(filename, None)

    @contextlib.contextmanager
    def _path_lock(self, path):
        lockfile = self._join_path(path, 'lock')
        with lock_utils.InterProcessLock(lockfile) as lock:
            with _storagefailure_wrapper():
                yield lock

    def _join_path(self, *parts):
        return os.path.join(*parts)

    def _get_item(self, path):
        with self._path_lock(path):
            item_path = self._join_path(path, 'metadata')
            return misc.decode_json(self._read_from(item_path))

    def _set_item(self, path, value, transaction):
        with self._path_lock(path):
            item_path = self._join_path(path, 'metadata')
            self._write_to(item_path, jsonutils.dumps(value))

    def _del_tree(self, path, transaction):
        with self._path_lock(path):
            shutil.rmtree(path)

    def _get_children(self, path):
        with _storagefailure_wrapper():
            return [link for link in os.listdir(path)
                    if os.path.islink(self._join_path(path, link))]

    def _ensure_path(self, path):
        with _storagefailure_wrapper():
            misc.ensure_tree(path)

    def _create_link(self, src_path, dest_path, transaction):
        with _storagefailure_wrapper():
            try:
                os.symlink(src_path, dest_path)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

    @contextlib.contextmanager
    def _transaction(self):
        """This just wraps a global write-lock."""
        lock = self.backend.lock.write_lock
        with lock():
            yield

    def validate(self):
        with _storagefailure_wrapper():
            for p in (self.flow_path, self.atom_path, self.book_path):
                if not os.path.isdir(p):
                    raise RuntimeError("Missing required directory: %s" % (p))
