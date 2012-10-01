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

    import tempfile
    path = tempfile.mkdtemp()
    print('path: ', path)
    c = cconfig.BoundCconfig(path, schema=schema)
    print(c)
    # change some properties
    c['changed'] = True
    c['code-remote'] = 'whatever'
    c['source'] = '/path/to/source'
    c['explorer'] = {'state': 'absent'}
    c['parameter'] = {'state': 'present'}
    c['state'] = 'done'
    # flush changes to disk
    c.sync()
    print(c)
    # implicit load/sync with context manager
    with c as _c:
        print(_c)
        _c['state'] = 'not-like-before'
    print(c)


if __name__ == '__main__':
    main()
