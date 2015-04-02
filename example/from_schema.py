#!/usr/bin/env python

import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

import os.path as op
import pprint
import sys
sys.path.insert(0, op.abspath(op.join(op.dirname(op.realpath(__file__)), '..')))

import cconfig


def main_(path):
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
    obj = cconfig.from_schema(schema)
    print(obj)
    obj['changed'] = True
    print('changed: ', obj['changed'])
    print('state: ', obj['state'])
    print('parameter[\'state\']: ', obj['parameter']['state'])
    print('explorer[\'state\']: ', obj['explorer']['state'])
    print(obj)
    import tempfile
    tmpdir = tempfile.mkdtemp()
    print('tmpdir: ', tmpdir)
    cconfig.to_dir(tmpdir, obj, schema=schema)


def main():
    schema_decl = (
        # path, type, subschema
        ('conf', 'mapping', (
            ('explorer', str),
            ('file', str),
            ('manifest', str),
            ('transport', str),
            ('type', str),
        )),
        ('explorer', dict, (
            ('state', str),
        )),
    )

    schema = cconfig.Schema(schema_decl)
    obj = cconfig.from_schema(schema)
    pprint.pprint(obj)


if __name__ == '__main__':
    main()
