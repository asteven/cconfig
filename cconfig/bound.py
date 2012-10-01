'''
(c) 2012 Steven Armstrong steven-cconfig@armstrong.cc

A cconfig [1] implementation for python.

[1] http://nico.schotteli.us/papers/linux/cconfig/
'''

import os
import collections
import logging
log = logging.getLogger(__name__)


import cconfig


class BoundCconfig(cconfig.Cconfig):
    """A cconfig object which is bound to a directory.
    """
    def __init__(self, path, schema):
        super(BoundCconfig, self).__init__(schema)
        self.path = path
        self._dirty = set()
        self.from_dir(self.path)

    def __getitem__(self, key):
        #log.debug('__getitem__: {}'.format(key))
        return super(BoundCconfig, self).__getitem__(key)

    def __setitem__(self, key, value):
        #log.debug('__setitem__: {} = {}'.format(key, value))
        if not key in self or value != self[key]:
            super(BoundCconfig, self).__setitem__(key, value)
            self._dirty.add(key)

    def sync(self):
        """Sync this cconfig object to disk.
        """
        if self._dirty:
            self.to_dir(self.path)

    def __enter__(self):
        self.sync()
        self.from_dir(self.path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sync()
        # we don't handle errors ourself
        return False
