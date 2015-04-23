'''
(c) 2012-2014 Steven Armstrong steven-cconfig@armstrong.cc

A cconfig [1] implementation for python.

[1] http://nico.schotteli.us/papers/linux/cconfig/

--------------------------------------------------------------------------------

data types:
    - string: value of file
    - int: value of file as int
    - boolean: file exists or not
    - list: lines of file as list
    - dict: folder with files
'''

import os
import collections
import tempfile
import shutil
import logging


class Error(Exception):
    """Base class for all Errors in this package
    """
    pass


def from_schema(schema, obj=None, keys=None):
    """Create a new empty object from the given schema.
    """
    log = logging.getLogger(__name__)
    log.debug('Creating cconfig from schema')
    _obj = obj or {}
    # if the user has given a list of keys, only work with those
    # otherwise use all keys in the schema.
    if keys:
        candidates = keys
    elif schema:
        candidates = schema.keys()
    for key in candidates:
        if schema:
            cconfig_type = schema[key]
        else:
            cconfig_type = default_cconfig_type
        _obj[key] = cconfig_type.from_schema()
        log.debug('< %s = %s %s', key, _obj[key], cconfig_type)
    return _obj


def from_dir(base_path, obj=None, schema=None, keys=None):
    log = logging.getLogger(__name__)
    log.debug('Loading cconfig from: %s', base_path)
    _obj = obj or {}
    # if the user has given a list of keys, only work with those
    # otherwise use all keys in the schema or all keys in base_path.
    if keys:
        candidates = keys
    elif schema:
        candidates = schema.keys()
    else:
        if os.path.isdir(base_path):
            candidates = os.listdir(base_path)
        else:
            candidates = []
    for key in candidates:
        if schema:
            cconfig_type = schema[key]
        else:
            cconfig_type = default_cconfig_type
        path = os.path.join(base_path, key)
        _obj[key] = cconfig_type.from_path(path)
        log.debug('< %s %s = %s %s', path, key, _obj[key], cconfig_type)
    return _obj


def to_dir(base_path, obj, schema=None, keys=None):
    log = logging.getLogger(__name__)
    log.debug('Saving cconfig to: %s', base_path)
    if not os.path.isdir(base_path):
        os.mkdir(base_path)
    # if the user has given a list of keys, only work with those
    # otherwise use all keys in given object.
    if keys:
        candidates = keys
    else:
        candidates = obj.keys()
    for key in candidates:
        if schema and key in schema:
            cconfig_type = schema[key]
        else:
            cconfig_type = default_cconfig_type
        path = os.path.join(base_path, key)
        value = obj.get(key, None)
        log.debug('> %s %s = %s %s', path, key, value, cconfig_type)
        cconfig_type.to_path(path, value)


class BoundDict(collections.MutableMapping):
    """A dictionary that is bound to a directory on disk.
    Also implements a context manager that serializes the object to disk when
    entered and loads it back when exited.

    Usage:
        d = {'a':1, 'b':2}
        b = BoundDict('/tmp/my-object', d)
        with b as o:
            do_something_that_changes_object_on_disk(o)
        assert 'c' in d 'dictionary now has new members'
    """
    def __init__(self, obj, path=None, schema=None, keys=None):
        super(BoundDict, self).__init__()
        self.path = path or tempfile.mkdtemp(prefix='cconfig.')
        self._obj = obj
        self._schema = schema
        self._keys = keys
        self._dirty = set()
        #for name in self.proxied_magic_member_names:
        #    setattr(self, name, getattr(self._obj, name))

    def __getattr__(self, name):
        """Delegate access to attributes which are not our own to the
        wrapped object.
        """
        return getattr(self._obj, name)


    def save(self, keys=None):
        if keys is None:
            keys = self._keys
        to_dir(self.path, self._obj, schema=self._schema, keys=keys)

    def load(self):
        from_dir(self.path, obj=self._obj, schema=self._schema, keys=self._keys)

    def delete(self):
        shutil.rmtree(self.path)

    def sync(self):
        """Write changed items to disk.
        Reload all items from disk.
        """
        if self._dirty:
            self.save(keys=self._dirty)
            self._dirty.clear()
        self.load()

    def __enter__(self):
        """When entering the context manager save object to disk.
        """
        self.save()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """When leaving the context manager load the object back from disk.
        """
        self.load()
        # we don't handle errors ourself
        return False

    ### implement mapping interface
    def __getitem__(self, key):
        return self._obj[key]

    def __setitem__(self, key, value):
        """Delegate to wrapped object, but remember what was changed.
        """
        if not key in self._obj or value != self._obj[key]:
            self._obj.__setitem__(key, value)
            # keep track of changes so only those can be flushed to disk
            self._dirty.add(key)

    def __delitem__(self, key):
        self._obj.__delitem__(key)

    def __iter__(self):
        return self._obj.__iter__()

    def __len__(self):
        return self._obj.__len__()
    ###/ implement mapping interface


def bind(obj, path=None, schema=None, keys=None):
    """Utility function to create a BoundDict.

    Usage:
        d = {'a':1, 'b':2}
        with cconfig.bind(d, path='/tmp/my-object') as o:
            do_something_that_changes_object_on_disk(o)
        assert 'c' in d 'dictionary now has new members'
    """
    return BoundDict(obj, path=path, schema=schema, keys=keys)


from .schema import Schema, default_cconfig_type
