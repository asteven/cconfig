'''
(c) 2012-2014 Steven Armstrong steven-cconfig@armstrong.cc

A cconfig [1] implementation for python.

[1] http://nico.schotteli.us/papers/linux/cconfig/
'''

import os
import glob
import collections
import logging
log = logging.getLogger(__name__)


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
        ('require', SomeCustomType),
        ('nested', dict, (
            ('first', str),
            ('second', int),
            ('third', dict, (
                ('alist', list),
                ('adict', dict),
            )),
        )),
    )

    """
    def __init__(self, schema=None):
        self._schema = schema or ()
        self._schema_map = collections.OrderedDict()
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

    def keys(self):
        return self._schema_map.keys()

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
        self.schema = Schema(schema=schema)

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
                if value:
                    fd.write(str(value) + '\n')
        except EnvironmentError as e:
            # error ignored
            pass

    def from_schema(self):
        return None


class BoolType(CconfigType):
    _type = bool

    def from_path(self, path):
        return os.path.isfile(path)

    def to_path(self, path, value):
        # True: file exists, False: file does not exist
        if value:
            open(path, 'w').close()
        elif os.path.isfile(path):
            os.unlink(path)


class StrType(CconfigType):
    _type = str

    def from_path(self, path):
        """Return the string stored in path or None if path doies not exist.
        """
        return self._read(path)

    def to_path(self, path, value):
        if value is not None:
            self._write(path, value)


class IntType(StrType):
    _type = int

    def from_path(self, path):
        try:
            return int(super().from_path(path))
        except TypeError:
            return None


class DateTimeType(StrType):
    """Datetime from unix timestamp in a file.
    TODO: maybe set/get file ctime instead of storing value inside file?
    """
    _type = 'datetime'

    def from_path(self, path):
        value = super(DateTimeType, self).from_path(path)
        if value:
            return datetime.datetime.fromtimestamp(float(value))

    def to_path(self, path, value):
        if value:
            super(DateTimeType, self).to_path(path, value.timestamp())


class ListType(CconfigType):
    """List from lines in a file.
    """
    _type = list

    def from_schema(self):
        return []

    def from_path(self, path):
        value = self._read(path)
        if value:
            return value.split('\n')
        else:
            return []

    def to_path(self, path, value):
        if value is not None:
            # value is a iterable, save as newline delimited string
            self._write(path, '\n'.join(value))


class ListDirType(CconfigType):
    """List from directory contents instead of from lines in a file.
    """
    _type = 'listdir'

    def from_schema(self):
        return []

    def from_path(self, path):
        try:
            return os.listdir(path)
        except EnvironmentError:
            return []

    def to_path(self, path, value):
        raise NotImplementedError('ListDirType is implemented read only, to_path not implemented.')


class DictType(CconfigType):
    """Dictionary from a directory, where file names are the keys and their
    content the values.
    """
    _type = dict

    def from_schema(self):
        _dict = { key: cconfig_type.from_schema()
            for key,cconfig_type in self.schema.items()
        }
        return _dict

    def from_path(self, path):
        if len(self.schema.keys()):
            return from_dir(path, schema=self.schema)
        else:
            return from_dir(path)

    def to_path(self, path, value):
        if value is not None:
            if len(self.schema.keys()):
                to_dir(path, value, schema=self.schema)
            else:
                to_dir(path, value)


class CollectionType(CconfigType):
    """List from directory contents where each item in the list is itself a
    cconfig object.
    """
    _type = 'collection'

    def from_schema(self):
        return []

    def from_path(self, path):
        collection = []
        for file_name in glob.glob1(path, '*'):
            file_path = os.path.join(path, file_name)
            o = from_dir(file_path, schema=self.schema)
            collection.append(o)
        return collection

    def to_path(self, path, collection):
        os.mkdir(path)
        if collection is not None:
            for item in collection:
                # use first name in the schema as the key to store it under
                key = self.schema.keys()[0]
                file_name = item[key]
                file_path = os.path.join(path, file_name)
                to_dir(file_path, item, schema=self.schema)


class MappingType(CconfigType):
    """A Mapping is a generic container for associating key/value pairs.

    Usage Example:
        schema_decl = (
            ('user', 'mapping', (
                ('first_name', str),
                ('last_name', str),
            ),
        )
        schema = cconfig.Schema(schema_decl)
        obj = {'user': {
                'john': {'first_name': 'John', 'last_name': 'Doe'}
            }
        }
        import tempfile
        path = tempfile.mkdtemp()
        to_dir(path, obj, schema=schema)
    """
    _type = 'mapping'

    def from_schema(self):
        mapping = { key: cconfig_type.from_schema()
            for key,cconfig_type in self.schema.items()
        }
        return mapping

    def from_path(self, path):
        mapping = {}
        for key in glob.glob1(path, '*'):
            cconfig_type = self.schema[key]
            file_path = os.path.join(path, key)
            value = cconfig_type.from_path(file_path)
            mapping[key] = value
        return mapping

    def to_path(self, path, mapping):
        if not os.path.isdir(path):
            os.mkdir(path)
        if mapping is not None:
            for key,value in mapping.items():
                cconfig_type = self.schema[key]
                file_path = os.path.join(path, key)
                cconfig_type.to_path(file_path, value)


from . import from_schema, from_dir, to_dir

default_cconfig_type = StrType()
