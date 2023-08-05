import sys
import os
import types
import io

"""
Tiffany - Tiff with PIL without PIL
===================================

This module implements reading and writing of Tiff files.
It uses a few files from PIL as sub-modules via import_mapper
and therefore can coexist with a seperate PIL installation.

The sole purpose of Tiffany is reading and writing of multi-file
Tiff. No attempt is made to encode, decode or modify image data.
Tags are normalized and cleaned as a side effect.


How it works
------------
-- to be done --


Background
----------

Tiffany originates in the Pydica project that needs to read
multi-file Tiff with CCITT G3/G4 encoding and display certain pages
in Qt (PySide). Qt decodes many formats, but cannot display more than
the first page and is very pedantic about the Tiff tags. Tiffany solves
exactly that problem and does not require temporary files.


Status
------

Tiffany now supports python 2.6, 2.7 and 3.2 .
"""

rootpath = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    sys.path.insert(0, os.path.join(rootpath, '..'))
    from tiffany import start_mapper
    start_mapper()

from tiffany import Image, TiffImagePlugin
from tiffany.compat import with_metaclass

class TiffanyCore:
    __module__ = 'Image.core'

    class FakeImage:
        def pixel_access(self, readonly):
            return SyntaxError('this value should not be used')

    def new(self, mode, size):
        im = self.FakeImage()
        im.mode = mode
        im.size = size
        return im

    class TiffanyDecoder:
        def __init__(self, mode, *args):
            self.mode = mode
            self.args = args

        def setimage(self, im, *args):
            self.im = im
            self.args = args

        def decode(self, block):
            # we ignore the read block and say 'ok'
            return -1, 0

    def tiffany_decoder(self, mode, *args):
        return self.TiffanyDecoder(mode, *args)

    def __getattr__(self, decoder_name):
        if decoder_name.endswith('_decoder'):
            return self.tiffany_decoder

    class TiffanyEncoder:
        def __init__(self, mode, src_fp, strips):
            self.mode = mode
            self.src_fp = src_fp
            self.strips = strips

        def setimage(self, im, *args):
            self.im = im
            self.args = args

        def encode_to_file(self, fh, bufsize):
            # we ignore the bufsize and just copy over
            # XXX modify that and implement a generator protocol!
            src = self.src_fp
            for ofs, lng in self.strips:
                src.seek(ofs)
                buf = src.read(lng)
                os.write(fh, buf)
            return 0

        def encode(self, bufsize):
            # we ignore the bufsize and just copy over
            # XXX modify that and implement a generator protocol!
            src = self.src_fp
            ret = src.read(0)  # compatible empty string/bytes
            for ofs, lng in self.strips:
                src.seek(ofs)
                buf = src.read(lng)
                ret += buf
            return None, 1, ret

    def tiffany_encoder(self, mode, source, *strips):
        """ this encoder blindly copies what it gets from the (equally blind)
        decoder """
        return self.TiffanyEncoder(mode, source, strips)


def func_with_new_globals(func, new_globals):
    """Make a copy of a function with new globals."""
    f = types.FunctionType(func.__code__, new_globals,
                           func.__name__, func.__defaults__,
                           func.__closure__)
    if func.__dict__:
        f.__dict__ = type(func.__dict__)()
        f.__dict__.update(func.__dict__)
    return f


# a handy metaclass that injects a class into a different module
class TiffanyMeta(type):
    def __new__(_mcs, _name, _bases, _dict):
        meth_globals = inject_into_module.__dict__

        ng = func_with_new_globals
        for name, func in _dict.items():
            if isinstance(func, types.FunctionType):
                _dict[name] = ng(func, meth_globals)
            elif isinstance(func, (staticmethod, classmethod)):
                _dict[name] = type(func)(ng(func.__func__, meth_globals))
            elif isinstance(func, property):
                _dict[name] = property(ng(func.fget, meth_globals))
        cls = type.__new__(_mcs, _name, _bases, _dict)
        meth_globals[_name] = cls
        return cls

Image.core = TiffanyCore()
inject_into_module = TiffImagePlugin


"""
Building python3 compatibility
------------------------------

In the case of the new io.BytesIO objects (supported in python 2.7,
required in python 3) we need a little wrapper that emulates the
StringIO behavior of raising AttributeError when accessing 'fileno'.
io.BytesIO raises io.UnsupportedOperation.
We fix that by a redirection which raises AttributeError.
"""


class BytesIOWrapper(with_metaclass(TiffanyMeta)):

    def __init__(self, bytesio):
        self._bytesio = bytesio

    def __getattr__(self, name):
        if name == 'fileno':
            raise AttributeError()
        return getattr(self._bytesio, name)


class TiffanyImageFile(TiffImagePlugin.TiffImageFile, with_metaclass(TiffanyMeta)):

    @staticmethod
    def _save_as_is(im, fp, filename):
        import os
        import io
        try:
            rawmode, prefix, photo, format, bits, extra = SAVE_INFO[im.mode]
        except KeyError:
            raise IOError("cannot write mode %s as TIFF" % im.mode)

        # making io.BytesIo compatible with old StringIO assumptions
        if isinstance(fp, io.BytesIO):
            fp = BytesIOWrapper(fp)

        ifd = ImageFileDirectory(prefix)

        # copy the original ifd.
        # it cannot be used directly, bug in the _save handler!
        # we also clean the strings from trailing nulls
        stripoffsets, stripbytecounts = None, None
        for tag, value in im.ifd.items():
            # do NOT use im.ift.tags.items because of lazy evaluation.
            if type(value[0]) == type(()) and len(value) == 1:
                assert tag in (X_RESOLUTION, Y_RESOLUTION)
                value = value[0]
            elif tag == STRIPOFFSETS:
                # don't carry over the old offsets
                stripoffsets = value
                # re-adjust the offsets to zero
                minvalue = min(value)
                value = tuple(v - minvalue for v in value) 
            elif tag == STRIPBYTECOUNTS:
                stripbytecounts = value
            elif tag == 293:  # T6Options
                # enforce type 4, see
                # http://partners.adobe.com/public/developer/en/tiff/TIFF6.pdf
                ifd.tagtype[tag] = 4  # LONG
            elif isinstance(value, bytes):
                value = value.rstrip(b'\0')
            ifd[tag] = value

        assert stripoffsets and stripbytecounts
        assert len(stripoffsets) == len(stripbytecounts)
        im.encoderconfig = tuple(zip(stripoffsets, stripbytecounts))

        # -- multi-page -- skip TIFF header on subsequent pages
        is_multipage = fp.tell() != 0
        if not is_multipage:
            # tiff header (write via IFD to get everything right)
            # PIL always starts the first IFD at offset 8
            fp.write(ifd.prefix + ifd.o16(42) + ifd.o32(8))

        savepos = fp.tell()
        offset = ifd.save(fp)

        ImageFile._save(im, fp, [
            ("tiffany", (0, 0) + im.size, offset, (im._TiffImageFile__fp, ))
            ])

        # A bigger problem with PIL was that it uses the file handle
        # internally,
        # and therefore the fp is not updated. We do that now:
        if hasattr(fp, 'fileno'):
            syncpos = os.lseek(fp.fileno(), 0, 1)  # emulated tell()
            fp.seek(syncpos, 0)

        # -- helper for multi-page save --
        if is_multipage:
            holdpos = fp.tell()
            fp.seek(im.last_linkoffset)
            fp.write(ifd.o32(savepos))
            fp.seek(holdpos)

        # -- find ifd's link position --
        im.last_linkoffset = savepos + 2 + len(ifd.tags) * 12

# override the already registered plugin
Image.register_open("TIFF", TiffanyImageFile, TiffImagePlugin._accept)
Image.register_save("TIFF", TiffanyImageFile._save_as_is)


class Tiffany(object):
    ''' the minimum interface to Tiffany:

    im = tiffany.open(fp)  -- opens an image, given the file name or open file
        a Tiffany object is returned.

    Methods of a Tiffany object:

    im.seek(frame)    -- seek the given frame in a multipage tiff

    im.tell()         -- return the current frame number

    im.save(fp)       -- write the current frame to a file
        fp can be a file name or an open file pointer.
        In the latter case, multiple saves to that fp create a multipage Tiff.
    '''

    def __init__(self, im):
        assert isinstance(im, Image.Image)
        self.im = im

    def seek(self, pos):
        self.im.seek(pos)

    def tell(self):
        return self.im.tell()

    def save(self, fp):
        self.im.save(fp, 'tiff')


def open(file_or_fp, mode='r'):
    im = Image.open(file_or_fp)
    return Tiffany(im)


def inline_test(fname, altpage):

    # reading from a file
    imfile = os.path.join(rootpath, 'test/data', fname)
    if not os.path.exists(imfile):
        print('warning: %s not found' % fname)
        return
    outfile = os.path.join(os.path.dirname(imfile), 'look_' + fname)
    im = open(imfile)

    #with io.open(outfile, 'wb') as imf:
        #for i in range(2):
            #im.seek(altpage)
            #im.save(imf)
            #im.seek(0)
            #im.save(imf)

    ## reading from a buffer
    #im = io.open(imfile, 'rb').read()
    #im = io.BytesIO(im)
    #im = open(im)

    with io.open(outfile, 'wb') as imf:
        for i in range(3):
            page = altpage
            while 0 and page >= 0:
                im.seek(page)
                im.save(imf)
                im.save(imf)
                im.save(imf)
                page -= 1
            page = 1
            while page <= altpage:
                im.seek(page)
                im.save(imf)
                im.save(imf)
                im.save(imf)
                page += 1 + 999 ###
                

    # writing to a buffer
    imf = io.BytesIO()
    for i in range(2):
        break ##!!
        im.seek(altpage)
        im.save(imf)
        im.seek(0)
        im.save(imf)

if __name__ == '__main__':
    inline_test('lzw_pon.tiff', 0)
    inline_test('recipe_1.tiff', 1)
    inline_test('multipage.tiff', 3)
    
