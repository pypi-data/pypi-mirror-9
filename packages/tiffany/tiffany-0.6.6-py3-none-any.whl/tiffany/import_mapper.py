"""
import mapper
=============

This is a prototype of a general import mapper for packages.
Right now it is specialized for handling PIL for Tiffany, but can
be extended to do a context mapping for any package.
"""

from __future__ import print_function

import sys
import os
import types

from os.path import normpath, join, dirname
from tiffany import compat  # side effect: defines builtins
import builtins

package_prefix = 'tiffany'
mapped_dir = normpath(join(dirname(__file__), 'from-pil-py3'))
mapped_modules = tuple(name[:-3] for name in os.listdir(mapped_dir)
                       if name.endswith('.py'))
orig__import = __import__


class MyImporter(object):

    def __call__(self, name, gl=None, lc=None, fl=None, lv=-1):
        self.args = (name, gl, lc, fl, lv)
        context_path = os.path.dirname(sys._getframe(1).f_code.co_filename)
        if context_path != mapped_dir:
            return orig__import(name, gl, lc, fl, 0)
        if name == '':
            # undoing the relative imports from the python3 patch
            assert fl and len(fl) == 1
            name, fl, lv = fl[0], None, 0
            is_from = True
        else:
            is_from = False
        origname = name
        mapped = False
        if name == 'FixTk':
            raise ImportError('hey these imports are weird! (ctypes?!)')
        if name == '_imaging':
            raise ImportError('we don\'t want no binaries')
        if name.endswith('ImagePlugin') and name not in wanted_plugins:
            raise ImportError('rejected unwanted plugin')
        if name in mapped_modules:
            # turn 'import Image' into 'from x.y import Image'
            fl = fl or []
            fl.append(name)
            truename = package_prefix + '.' + name
            self.args = (package_prefix, gl, lc, fl, lv)
            orig__import(package_prefix, gl, lc, fl, lv)
            retname = package_prefix if is_from else truename
            ret = sys.modules[retname]
        else:
            ret = orig__import(name, gl, lc, fl, lv)
        return ret

wanted_plugins = ['TiffImagePlugin']


def install_mapper():
    builtins.__import__ = MyImporter()


def uninstall_mapper():
    builtins.__import__ = orig__import
