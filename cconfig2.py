
'''

- Cconfig should not depend on filesystem
- explicit load/save to/from disk



obj = Cconfig.load_from_dir('/path/to/dir')
# or
obj = Cconfig()
obj.load('/path/to/dir')

obj.whatever = False
obj.save_to('/path/to/other/dir')


--------------------------------------------------------------------------------

data types:
    - string: value of file
    - int: value of file as int
    - boolean: file exists or not
    - list: lines of file as list


path            type        class
---------------------------------
asteven         dict        CconfigDict
asteven/gid     int         CconfigInt
asteven/groups  list        CconfigList
asteven/name    str         CconfigString
asteven/uid     int         CconfigInt
is_staff        bool        CconfigBoolean

asteven.gid = 5
asteven.groups = ['list', 'of', 'strings']
asteven.name = 'Steven Armstrong'
asteven.uid = 42
asteven.is_staff = True

'''

import os
import collections
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class CconfigError(Exception):
    pass


class AbsolutePathRequiredError(CconfigError):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return 'Absolute path required, got: %s' % self.path


class CconfigObject(object):
    def __init__(self, path, schema):
        self._path = os.path.realpath(path)
        self._schema = schema
        if not os.path.isabs(self._path):
            raise AbsolutePathRequiredError(self._path)

    def __repr__(self):
        return '<%s path=%s>' % (self.__class__.__name__, self.path)


class Cconfig2(CconfigObject):
    def __getitem__(self, key):
        logging.debug('key: %s', key)
        key_path = os.path.join(self._path, key)
        logging.debug('key_path: %s', key_path)
        try:
            _type = self._schema._types[key]
            _class = self._schema._classes[key]
            _instance = _class(key_path)
            with open(self.path, 'r') as fd:
                _instance = _class(fd)
            return _instance
        except KeyError as er:
            raise KeyError(key)

    def _get_path(self, segment):
        return os.path.join(self._path, segment)

    def __read(self):
        value = None
        # if file does not exist return empty list
        try:
            with open(self.path) as fd:
                value = fd.read()
        except EnvironmentError as e:
            # error ignored
            pass
        return value

    def __write(self, value):
        try:
            with open(self.path, 'w') as fd:
                fd.write(str(value))
        except EnvironmentError as e:
            # error ignored
            pass


'''
changed             boolean
code-remote         string
explorer            dict
explorer/state      string
parameter           dict
parameter/state     string
source              list
state               string

--------------------------------------------------------------------------------

{
    ''
}

'''

SchemaItem = collections.namedtuple('SchemaItem', ('type_', 'subschema'))
class CconfigSchema(object):
    def __init__(self, schema=None):
        self._schema = schema or ()
        self._schema_map = {}
        self._types = {}
        self._classes = {}
        for entry in self._schema:
            assert len(entry) >= 2
            subschema = None
            if len(entry) == 2:
                key, type_ = entry
            elif len(entry) == 3:
                key, type_, subschema = entry
            self._schema_map[key] = SchemaItem(type_=type_, subschema=subschema)

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


class CdistDependcyEntry(object):
    def __init__(self, value):
        self.source, self.value = value.split(':')
    def __str__(self):
        return '%s:%s' % (self.source, self.value)


schema_decl = (
    # path, type, reader/writer, subschema
    ('changed', bool),
    ('code-remote', str),
    ('source', str),
    ('explorer', dict, (
        ('state', str),
    )),
    ('parameter', dict),
#    ('parameter', dict, (
#        ('state', str),
#    )),
    #('require', list, CdistDependcyEntry),
    ('state', str),
#    ('nested', dict, None, (
#        ('first', str),
#        ('second', int),
#        ('third', dict, None, (
#            ('alist', list),
#            ('adict', dict),
#        )),
#    )),
)

schema = CconfigSchema(schema_decl)

import collections

class Cconfig(collections.MutableMapping):
    def __init__(self, schema=None, strict=False):
        self.schema = schema or CconfigSchema()
        self.strict = strict
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
        self._date.update(other)

    def __repr__(self):
        return '<{} {}>'.format(self.__class__.__name__, self._data)

    def __read(self, path):
        value = None
        # if file does not exist return None
        try:
            with open(path, 'r') as fd:
                value = fd.read()
        except EnvironmentError as e:
            # error ignored
            pass
        return value

    def __write(self, path, value):
        try:
            with open(path, 'w') as fd:
                fd.write(str(value))
        except EnvironmentError as e:
            # error ignored
            pass

    def get_schema(self, key):
        try:
            return self.schema[key]
        except KeyError:
            if not self.strict:
                return SchemaItem(type_=str, subschema=None)
            else:
                # FIXME: wrap in custom exception
                raise

    def from_dir(self, base_path):
        logger.debug('from_dir: %s', base_path)
        for key in os.listdir(base_path):
            logger.debug('key: %s', key)
            path = os.path.join(base_path, key)
            logger.debug('path: %s', path)
            if os.path.isfile(path):
                # read property value from file
                schema = self.get_schema(key)
                value = self.__read(path)
                if value:
                    value = value.strip('\n')
                logger.debug('value: %s', value)
                self._data[key] = schema.type_(value)
            elif os.path.isdir(path):
                # create new child cconfig object and dispatch
                schema = self.schema[key]
                o = self.__class__(CconfigSchema(schema.subschema), strict=self.strict)
                o.from_dir(path)
                self._data[key] = o
            else:
                raise ValueError('File type of %s not supported'.format(path))
        
    def to_dir(self, base_path):
        if not os.path.isdir(base_path):
            os.mkdir(base_path)
        logger.debug('to_dir: %s', base_path)
        for key,value in self.items():
            logger.debug('%s = %s', key, value)
            # read property value from file
            type_ = type(value)
            logger.debug('type: %s', type_)
            path = os.path.join(base_path, key)
            logger.debug('path: %s', path)
            if isinstance(value, Cconfig):
                value.to_dir(path)
            elif isinstance(value, collections.MutableMapping):
                schema = self.get_schema(key)
                o = self.__class__(CconfigSchema(schema.subschema), strict=self.strict)
                o.update(value)
                o.to_dir(path)
            elif isinstance(value, bool):
                if value:
                    open(path, 'w').close()
            elif isinstance(value, collections.MutableSequence):
                self.__write(path, '\n'.join(value))
            else:
                # save as string
                if value:
                    self.__write(path, '{}\n'.format(value))


def main2(path):
    c = Cconfig(path, schema)
    print('changed: ', c['changed'])
    
def main(path):
    c = Cconfig(schema)
    #c = Cconfig()
    c.from_dir(path)
    print(c)
    #c['changed'] = True
    #print('changed: ', c['changed'])
    #print('state: ', c['state'])
    #print('parameter[\'state\']: ', c['parameter']['state'])
    #print('explorer[\'state\']: ', c['explorer']['state'])
    #print(c)
    import tempfile
    tmpdir = tempfile.mkdtemp()
    print('tmpdir: ', tmpdir)
    c.to_dir(tmpdir)

if __name__ == '__main__':
    import os.path as op
    import sys
    if len(sys.argv) > 1:
        test_dir = op.abspath(sys.argv[1])
    else:
        test_dir = op.abspath(op.join(op.dirname(__file__), 'cconfig_dir'))
    main(test_dir)


'''
schema = CconfigSchema()
schema.changed = CconfigBoolean
schema.code_remote = CconfigString
schema.explorer = CconfigDict
schema.explorer['state'] = CconfigString
schema.parameter = CconfigDict
schema.parameter['state'] = CconfigString
schema.state = CconfigString
'''




