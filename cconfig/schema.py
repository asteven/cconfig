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


class Schema(object):
    """
    schema_decl = (
        # path, type, subschema_decl
        ('changed', bool),
        ('code-remote', str),
        ('source', str),
        ('explorer', dict, (
            ('state', str),
        )),
        ('parameter', dict, (
            ('state', str),
        )),
        ('require', SomeCustomCconfigType),
        ('nested', dict, (
            ('first', str),
            ('second', int),
            ('third', dict, None, (
                ('alist', list),
                ('adict', dict),
            )),
        )),
    )

    """
    def __init__(self, schema=None):
        self._schema = schema or ()
        self._schema_map = {}
        self.__type_map = None
        for entry in self._schema:
            assert len(entry) >= 2
            subschema = None
            if len(entry) == 2:
                key, type_ = entry
            elif len(entry) == 3:
                key, type_, subschema = entry
            cconfig_type = self.type_map[type_]
            self._schema_map[key] = cconfig_type(schema=subschema)

    def __contains__(self, key):
        return key in self._schema_map

    def __getitem__(self, key, default=None):
        try:
            return self._schema_map[key]
        except KeyError:
            if default:
                return default
            else:
                raise

    def __iter__(self):
        return iter(self._schema_map.keys())

    def items(self):
        return self._schema_map.items()

    @property
    def type_map(self):
        if not self.__type_map:
            subclasses = CconfigType.__subclasses__()
            for subclass in subclasses:
                subclasses.extend(subclass.__subclasses__())
            self.__type_map = dict((getattr(subclass, '_type', subclass), subclass) for subclass in subclasses)
        return self.__type_map


class CconfigType(object):

    def __init__(self, schema=None):
        self.schema = schema

    def __str__(self):
        return self.__class__.__name__

    def _read(self, path):
        value = None
        # if file does not exist return None
        try:
            with open(path, 'r') as fd:
                value = fd.read().strip('\n')
        except EnvironmentError as e:
            # error ignored
            pass
        return value

    def _write(self, path, value):
        try:
            with open(path, 'w') as fd:
                fd.write(str(value) + '\n')
        except EnvironmentError as e:
            # error ignored
            pass


class BoolCconfigType(CconfigType):
    _type = bool

    def from_path(self, path):
        return os.path.isfile(path)

    def to_path(self, path, value):
        # True: file exists, False: file does not exist
        if value:
            open(path, 'w').close()
        elif os.path.isfile(path):
            os.unlink(path)


class StrCconfigType(CconfigType):
    _type = str

    def from_path(self, path):
        return self._read(path)

    def to_path(self, path, value):
        if value is not None:
            self._write(path, value)


class IntCconfigType(StrCconfigType):
    _type = int

    def from_path(self, path):
        return int(super(IntType, self).from_path(path))


class ListCconfigType(CconfigType):
    """List from lines in a file.
    """
    _type = list

    def from_path(self, path):
        value = self._read(path)
        if value:
            return value.split('\n')
        else:
            return []

    def to_path(self, path, value):
        if value is not None:
            if not isinstance(value, collections.MutableSequence):
                value = []
            # value is a list, save as newline delimited string
            self._write(path, '\n'.join(value))


class ListDirCconfigType(cconfig.schema.CconfigType):
    """List from directory contents instead of from lines in a file.
    """

    def from_path(self, path):
        try:
            return os.listdir(path)
        except EnvironmentError:
            return []

    def to_path(self, path, value):
        pass


class DictCconfigType(CconfigType):
    _type = dict

    def from_path(self, path):
        o = cconfig.Cconfig(schema=Schema(self.schema))
        o.from_dir(path)
        return o

    def to_path(self, path, value):
        if value is not None:
            if isinstance(value, cconfig.Cconfig):
                # value is a cconfig object, delegate serialization to it
                value.to_dir(path)
            elif isinstance(value, collections.MutableMapping):
                # value is a dictionary, create a cconfig object and delegate serialization to it
                o = cconfig.Cconfig(schema=Schema(self.schema))
                o.update(value)
                o.to_dir(path)
