"""
compat.py should be imported first.
It does certain patches and modifications for Python2 backward compatibility.
"""

import sys
import types
import operator
import collections
import string

# general python3 stuff
if sys.version_info[0] < 3:
    import __builtin__ as builtins
    sys.modules['builtins'] = builtins
else:
    import builtins

# compatibility helper for Python 2.6
if sys.version_info[:2] < (2, 7):
    def _patch():
        class classmethod(builtins.classmethod):
            __func__ = property(lambda self: self.im_func)
        builtins.classmethod = classmethod

        class staticmethod(builtins.staticmethod):
            __func__ = property(lambda self: self.__get__(0))
        builtins.staticmethod = staticmethod
    _patch()
    del _patch

#
# circumventing the metaclass notation difference between py2 and py3
# (borrowed from the "six" module)


def with_metaclass(meta, base=object):
    """Create a base class with a metaclass."""
    return meta("NewBase", (base,), {})


#
# emulating int.from_bytes and int.to_bytes for python 2
class _Int(int):
    ''' Simple implementation of python 3.2 methods.
        Can be made more general, but enough for tiffany
    '''

    @classmethod
    def from_bytes(cls, bytes_, byteorder, signed=False):  # '*' ignored
        c = bytes_
        if signed:
            raise NotImplementedError('signed is not implemented')
        lng = len(bytes_)
        if byteorder == 'little':
            if lng == 2:
                return ord(c[0]) + (ord(c[1]) << 8)
            if lng == 4:
                return (ord(c[0]) + (ord(c[1]) << 8) + (ord(c[2]) << 16) + 
                       (ord(c[3]) << 24))
        elif byteorder == 'big':
            if lng == 2:
                return ord(c[1]) + (ord(c[0]) << 8)
            if lng == 4:
                return (ord(c[3]) + (ord(c[2]) << 8) + (ord(c[1]) << 16) + 
                       (ord(c[0]) << 24))
        else:
            raise ValueError("byteorder must be either 'little' or 'big'")
        raise NotImplementedError("size other than 2 or 4 not implemented")

    def to_bytes(self, lng, byteorder, signed=False):  # '*' ignored
        i = self
        if signed:
            raise NotImplementedError('signed is not implemented')
        if byteorder == 'little':
            if lng == 2:
                return chr(i & 255) + chr(i >> 8 & 255)
            if lng == 4:
                return (chr(i & 255) + chr(i >> 8 & 255) + 
                       chr(i >> 16 & 255) + chr(i >> 24 & 255))
        elif byteorder == 'big':
            if lng == 2:
                return chr(i >> 8 & 255) + chr(i & 255)
            if lng == 4:
                return (chr(i >> 24 & 255) + chr(i >> 16 & 255) + 
                       chr(i >> 8 & 255) + chr(i & 255))
        else:
            raise ValueError("byteorder must be either 'little' or 'big'")
        raise NotImplementedError("size other than 2 or 4 not implemented")


if hasattr(int, 'from_bytes'):
    int = int
else:
    int = _Int

'''
Remark:
I could have been more rigorous and overwrite the builtins.int type
with the new derived class. Then we could write

    ol16 = lambda i: i.to_bytes(2, byteorder='little')

instead of

    ol16 = lambda i: int(i).to_bytes(2, byteorder='little')

Maybe later. Right now I'm reluctant, in the fear to produce
problems in applications just to make the code nicer.
'''
