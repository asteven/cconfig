#!/usr/bin/env python

import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

import os.path as op
import sys
sys.path.insert(0, op.abspath(op.join(op.dirname(op.realpath(__file__)), '..')))

import cconfig


def main(path):
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


if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_dir = op.abspath(sys.argv[1])
    else:
        test_dir = op.abspath(op.join(op.dirname(__file__), 'cconfig_dir/object/__start_on_boot/openvswitch/.cdist'))
    main(test_dir)
