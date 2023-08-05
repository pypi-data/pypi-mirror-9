# -*- coding: utf-8 -*-
import sys
sys.path.append('/Users/miburr/git/stnbu/npconf')

import sys
import os
import npconf
import types
from StringIO import StringIO

try:
    import unittest2 as unittest
except ImportError:
    import unittest

class ItemAttrDict(dict):

    def __init__(self, *args, **kwargs):
        super(ItemAttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def get_fstringio():
    def fstringio__init__(self, buf=''):
        self.buf = buf
        self.len = len(buf)
        self.buflist = []
        self.pos = 0
        self.softspace = 0
    new_dict = dict(StringIO.__dict__)
    new_dict['__init__'] = fstringio__init__
    new_dict['closed'] = False
    del new_dict['__module__']
    return type('fStringIO', (types.FileType,), new_dict)

fStringIO = get_fstringio()

init = fStringIO("""
os
ConfigSpace
ConfigValue
root.init2 = 'init2'
""")

config = """
root.foo = 'foo'
root.myspace.three.snap = 7
#root.myspace.three.foo2 = None
root.myspace.foo = 'foo'
"""

real_config_file_path = '/dev/null'

class TestAll(unittest.TestCase):

    def setUp(self):
        self.files = ItemAttrDict(
            init=init,
            user=config,
        )


    def test_all(self):

        d = 'DEFAULT'
        root_ = npconf.ConfigValue(name='root', data={'init': 'init'}, paths=[self.files.init])
        root_.update(data={'xxxxxx': None, 'foo': d})
        myspace = npconf.ConfigValue(
            name='myspace',
            data={
                'foo': d,
                'bar': d,
                'baz': d,
            })
        three = npconf.ConfigValue(name='three', data={'snap': None})
        three.configure(real_config_file_path)
        myspace.update({'three': three})
        root_.update({'myspace': myspace, 'xx': 'xx'})
        yourspace = npconf.ConfigValue(
            name='yourspace',
            data={
                'bar': d,
            }
        )
        root_.update({'yourspace': yourspace})
        root_.configure(self.files.user)

        assert root_.root == root_.store

        myspace['baz'] = 'xx'

        root = root_.config
        root.myspace.three.snap = 'x'
        three.update({'snap7':7})
        root.myspace.three.snap7 = 'x'

        with self.assertRaises(npconf.NewAttributesNotAllowed):
            root.myspace.three.whatever_whatever_zyx = complex()*20

if __name__ == '__main__':
   unittest.main()
