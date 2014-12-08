#!/usr/bin/env python
#
# Example of using a BoundCconfig
#

import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

import os.path as op
import sys
sys.path.insert(0, op.abspath(op.join(op.dirname(op.realpath(__file__)), '..')))

import cconfig 

def main():
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
        ('state', str),
    )

    schema = cconfig.Schema(schema_decl)
    d = cconfig.from_schema(schema)
    print(d)
    # set some properties
    d['changed'] = True
    d['code-remote'] = 'whatever'
    d['source'] = '/path/to/source'
    d['explorer'] = {'state': 'absent'}
    d['parameter'] = {'state': 'present'}
    d['state'] = 'done'

    import tempfile
    path = tempfile.mkdtemp()
    print('path: ', path)
    obj = cconfig.bind(d, path, schema=schema)
    print(obj)
    # implicit load/sync with context manager
    with obj as _o:
        print(_o)
        _o['state'] = 'not-like-before'
        _o.save()
    print(obj)


if __name__ == '__main__':
    main()
