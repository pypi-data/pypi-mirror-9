# tiffany tests

# for a basic test, simply run tiffany/monkeypil.py as a main program.

# adding tests for nicer byte functions under python 3.2

import pytest  # ensure presence of pytest
import sys
from os.path import dirname, join

# the existing working version, copied into a class
class v0_6(object):
    if sys.version_info[0] >= 3:
        def il16(c,o=0):
            return c[o] + (c[o+1] << 8)
        def il32(c,o=0):
            return c[o] + (c[o+1] << 8) + (c[o+2] << 16) + (c[o+3] << 24)
        def ol16(i):
            return bytes((i&255, i >> 8&255))
        def ol32(i):
            return bytes((i&255, i >> 8&255, i >> 16&255, i >> 24&255))
        
        def ib16(c,o=0):
            return c[o+1] + (c[o] << 8)
        def ib32(c,o=0):
            return c[o+3] + (c[o+2] << 8) + (c[o+1] << 16) + (c[o] << 24)
        def ob16(i):
            return bytes((i >> 8&255, i&255))
        def ob32(i):
            return bytes((i >> 24&255, i >> 16&255, i >> 8&255, i&255))
    else:
        def il16(c,o=0):
            return ord(c[o]) + (ord(c[o+1])<<8)
        def il32(c,o=0):
            return ord(c[o]) + (ord(c[o+1])<<8) + (ord(c[o+2])<<16) + (ord(c[o+3])<<24)
        def ol16(i):
            return chr(i&255) + chr(i>>8&255)
        def ol32(i):
            return chr(i&255) + chr(i>>8&255) + chr(i>>16&255) + chr(i>>24&255)
        
        def ib16(c,o=0):
            return ord(c[o+1]) + (ord(c[o])<<8)
        def ib32(c,o=0):
            return ord(c[o+3]) + (ord(c[o+2])<<8) + (ord(c[o+1])<<16) + (ord(c[o])<<24)
        def ob16(i):
            return chr(i>>8&255) + chr(i&255)
        def ob32(i):
            return chr(i>>24&255) + chr(i>>16&255) + chr(i>>8&255) + chr(i&255)
        
        for name, meth in locals().items():
            if not name.startswith('__'):
                locals()[name] = staticmethod(meth)

try:
    import tiffany
except ImportError:
    # when run from the source
    tiffanydir = join(dirname(__file__), '..', '..')
    sys.path.insert(0, tiffanydir)

from tiffany.TiffImagePlugin import *
from random import randint
TEST_ARR = bytes(randint(0, 255) for i in range(8))

def _check(f1, f2, lng, g1, g2):
    for ofs in range(len(TEST_ARR) - lng + 1):
        v, w = f1(TEST_ARR, ofs), f2(TEST_ARR, ofs)
        assert v == w
        assert g1(v) == g2(w)

def test_l16():
    _check(il16, v0_6.il16, 2, ol16, v0_6.ol16)

def test_l32():
    _check(il32, v0_6.il32, 4, ol32, v0_6.ol32)

def test_b16():
    _check(ib16, v0_6.ib16, 2, ob16, v0_6.ob16)

def test_b32():
    _check(ib32, v0_6.ib32, 4, ob32, v0_6.ob32)

