'''
(c) 2012 Steven Armstrong steven-cconfig@armstrong.cc

A cconfig [1] implementation for python.

[1] http://nico.schotteli.us/papers/linux/cconfig/

--------------------------------------------------------------------------------

- Cconfig should not depend on filesystem
- explicit load/save to/from disk

data types:
    - string: value of file
    - int: value of file as int
    - boolean: file exists or not
    - list: lines of file as list
    - dict: folder with files
'''

import os
import collections
import logging
log = logging.getLogger(__name__)


class Cconfig(collections.MutableMapping):
    def __init__(self, schema):
        self.schema = schema
        self._data = dict()

    def __getitem__(self, key):
        return self._data[key]    

    def __setitem__(self, key, value):
        self._data[key] = value

    def __delitem__(self, key):
        del self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def update(self, other):
        self._data.update(other)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self._data)

    def from_dir(self, base_path, keys=None, changed_since=None):
        self.clear()
        log.debug('Loading cconfig object from: {}'.format(base_path))
        # if the user has given a list of keys, only work with those
        # otherwise use all keys.
        candidates = keys or self.schema.keys()
        for key in candidates:
            cconfig_type = self.schema[key]
            path = os.path.join(base_path, key)
            self[key] = cconfig_type.from_path(path)
            #log.debug('< {} {} = {} {}'.format(path, key, self[key], cconfig_type._type.__name__))
            log.debug('< {} {} = {} {}'.format(path, key, self[key], cconfig_type))

    def to_dir(self, base_path, keys=None):
        if not os.path.isdir(base_path):
            os.mkdir(base_path)
        log.debug('Saving cconfig object to: {}'.format(base_path))
        # if the user has given a list of keys, only work with those
        # otherwise use all keys.
        candidates = keys or self.schema.keys()
        for key in candidates:
            cconfig_type = self.schema[key]
            path = os.path.join(base_path, key)
            value = self.get(key, None)
            #log.debug('> {} {} = {} {}'.format(path, key, value, cconfig_type._type.__name__))
            log.debug('> {} {} = {} {}'.format(path, key, value, cconfig_type))
            cconfig_type.to_path(path, value)
