'''
- Cconfig should not depend on filesystem
- explicit load/save to/from disk


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
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

class CconfigError(Exception):
    pass


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
        log.debug('from_dir: %s', base_path)
        for key in os.listdir(base_path):
            log.debug('key: %s', key)
            path = os.path.join(base_path, key)
            log.debug('path: %s', path)
            if os.path.isfile(path):
                # read property value from file
                schema = self.get_schema(key)
                value = self.__read(path)
                if value:
                    value = value.strip('\n')
                log.debug('value: %s', value)
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
        log.debug('to_dir: %s', base_path)
        for key,value in self.items():
            log.debug('%s = %s', key, value)
            # read property value from file
            type_ = type(value)
            log.debug('type: %s', type_)
            path = os.path.join(base_path, key)
            log.debug('path: %s', path)
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


def main(path):
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
