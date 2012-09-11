# -*- coding: utf-8 -*-
#
# Python module for working with cconfig [1] configuration trees.
# Currently only reading is implemented.
#
# (c) 2009, Steven Armstrong, ETH Zurich
#

import logging
log_file = '/tmp/cconfig.log'
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s', filename=log_file, filemode='a')
#logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s: %(message)s', filename=log_file, filemode='a')


import os


class CconfigBase(object):
    def __init__(self, path):
        self.path = os.path.realpath(path)

    def __repr__(self):
        return '<%s path=%s>' % (self.__class__.__name__, self.path)



class CconfigObject(CconfigBase):
    def __init__(self, path):
        super(CconfigObject, self).__init__(path)

    def __getitem__(self, key):
        child_path = os.path.join(self.path, key)
        if os.path.islink(child_path):
            return CconfigLink(child_path)
        elif os.path.isdir(child_path):
            return CconfigObject(child_path)
        elif os.path.isfile(child_path):
            return CconfigAttribute(child_path)
        else:
            raise KeyError(key)

    #def __setitem__(self, key, value):
    #    print '__setitem__: %s = %s' % (key, value)
    #    if isinstance(value, CconfigObject):
    #        pass


class CconfigAttribute(CconfigBase):
    def __init__(self, path, value=None):
        super(CconfigAttribute, self).__init__(path)
        #if value:
        #    f = open(self.path, 'w')
        #    f.write(str(value))
        #    f.close()

    def read(self):
        f = open(self.path, 'r')
        value = f.read()
        f.close()
        return value

    def write(self):
        pass

    def __str__(self):
        return self.read()


class CconfigLink(CconfigBase):
    pass

class Cconfig(CconfigObject):
    pass


def main(path):
    c = Cconfig(path)
    print '/', c
    print '/host/:', c['host']
    print '/host/coeus.inf.ethz.ch:', c['host']['coeus.inf.ethz.ch']
    print '/host/coeus.inf.ethz.ch/ip:', c['host']['coeus.inf.ethz.ch']['ip']
    print '/host/coeus.inf.ethz.ch/user:', c['host']['coeus.inf.ethz.ch']['user']
    print '/user/:', c['user']
    print '/user/asteven:', c['user']['asteven']



'''
data types:
    - string: value of file
    - int: value of file as int
    - boolean: file exists or not
    - list: lines of file as list
    - dict:
        
'''

if __name__ == '__main__':
    import os.path as op
    test_dir = op.abspath(op.join(op.dirname(__file__), 'cconfig_dir'))
    main(test_dir)


