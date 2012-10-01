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


import cconfig


class Cconfig(collections.MutableMapping):
    def __init__(self, schema=None, enforce_schema=False, ignore_unknown=False):
        self.schema = schema or cconfig.Schema()
        if enforce_schema and ignore_unknown:
            log.warn('enforce_schema overrides ignore_unkown')
        self.enforce_schema = enforce_schema
        self.ignore_unknown = ignore_unknown
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

    def __read(self, path):
        value = None
        # if file does not exist return None
        try:
            with open(path, 'r') as fd:
                value = fd.read().strip('\n')
        except EnvironmentError as e:
            # error ignored
            pass
        return value

    def __write(self, path, value):
        try:
            with open(path, 'w') as fd:
                fd.write(str(value) + '\n')
        except EnvironmentError as e:
            # error ignored
            pass

    def get_schema(self, key):
        try:
            return self.schema[key]
        except KeyError:
            if not self.enforce_schema:
                return cconfig.SchemaItem(type=str, subschema=None)
            else:
                raise

    def from_dir(self, base_path):
        self.clear()
        log.debug('Loading cconfig object from: {}'.format(base_path))
        for key,schema in self.schema.items():
            path = os.path.join(base_path, key)

            if issubclass(schema.type, bool):
                # value is a boolean, True: file exists, False: file does not exist
                self[key] = os.path.isfile(path)
            elif issubclass(schema.type, collections.MutableMapping):
                # create new child cconfig object and dispatch parsing/loading to it
                #o = self.__class__(schema=Schema(schema.subschema))
                o = Cconfig(schema=cconfig.Schema(schema.subschema))
                o.from_dir(path)
                self[key] = o
            else:
                # read property value from file
                value = self.__read(path)
                if issubclass(schema.type,collections.MutableSequence):
                    if value:
                        value = value.split('\n')
                    else:
                        value = []
                # cast to type using schema
                self[key] = schema.type(value)
            log.debug('< {} {} = {} {}'.format(path, key, self[key], schema.type))

    def to_dir(self, base_path):
        if not os.path.isdir(base_path):
            os.mkdir(base_path)
        log.debug('Saving cconfig object to: {}'.format(base_path))
        for key,schema in self.schema.items():
            path = os.path.join(base_path, key)
            value = self[key]
            log.debug('> {} {} = {} {}'.format(path, key, value, schema.type))

            if issubclass(schema.type, bool):
                # value is a boolean, True: file exists, False: file does not exist
                if value:
                    open(path, 'w').close()
                elif os.path.isfile(path):
                    os.unlink(path)
            elif issubclass(schema.type, collections.MutableMapping):
                if isinstance(value, Cconfig):
                    # value is a cconfig object, delegate serialization to it
                    value.to_dir(path)
                elif isinstance(value, collections.MutableMapping):
                    # value is a dictionary, create a cconfig object and delegate serialization to it
                    o = Cconfig(schema=cconfig.Schema(schema.subschema))
                    o.update(value)
                    o.to_dir(path)
            elif issubclass(schema.type,collections.MutableSequence):
                if not isinstance(value, collections.MutableSequence):
                    value = []
                # value is a list, save as newline delimited string
                self.__write(path, '\n'.join(value))
            else:
                # just save as string
                if value:
                    self.__write(path, value)
                elif os.path.isfile(path):
                    os.unlink(path)
