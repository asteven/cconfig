'''
(c) 2012 Steven Armstrong steven-cconfig@armstrong.cc

A cconfig [1] implementation for python.

[1] http://nico.schotteli.us/papers/linux/cconfig/
'''

import collections
import logging
log = logging.getLogger(__name__)


SchemaItem = collections.namedtuple('SchemaItem', ('type', 'subschema'))

class Schema(object):
    """
    schema_decl = (
        # path, type, subschema
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
        self._types = {}
        self._classes = {}
        for entry in self._schema:
            assert len(entry) >= 2
            subschema = None
            if len(entry) == 2:
                key, type_ = entry
            elif len(entry) == 3:
                key, type_, subschema = entry
            self._schema_map[key] = SchemaItem(type=type_, subschema=subschema)

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
