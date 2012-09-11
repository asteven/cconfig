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

    c = cconfig.Cconfig(schema, enforce_schema=True)
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
    if len(sys.argv) > 1:
        test_dir = op.abspath(sys.argv[1])
    else:
        test_dir = op.abspath(op.join(op.dirname(__file__), 'cconfig_dir/object/__start_on_boot/openvswitch/.cdist'))
    main(test_dir)
