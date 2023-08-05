
Tiffany - Read/Write Multipage-Tiff with PIL without PIL
========================================================

Tiffany stands for any tiff. The tiny module solves a large set of
problems, has no dependencies and just works wherever Python works.
Tiffany was developed in the course of the *Pydica* project and will
now appear on PyPi.

Abstract
========

During the development of *Pydica* (Python Distributed Capture) we were
confronted with the problem to read multipage Tiff scans. The GUI toolkit
*PySide (Qt)* does support Tiff, but only shows the first page. We also had
to support Fax compression (CCITT G3/G4), but *Qt* supports this.

As a first approach we copied single pages out of multi-page tiff files
using *tiffcp* or *tiffutil* (OS X) as a temp file for display. A sub-optimum
solution, especially for data security reasons.

The second approach replaced this by a tiny modification of the linkage of
the tiff directories (IFD). This way, a tiff file could be patched in memory
with the wanted page offset and then be shown without any files involved.

Unfortunately also this solution was not satisfactory:

- our tiff files have anomalies in their tiff tags like too many null-bytes
  and wrong tag order,

- Qt's implementation of tiff is over-pedantic and ignores all tags after the
  smallest error.
  
Being a good friend of *Fredrik Lundh* and his *PIL* since years, I tried to
attack the problem using this. Sadly Fredrik hasn't worked much on this since
2006, and the situation is slightly messed up:

*PIL* has a clean-up of tiff tags, but cannot cope with fax compression by default.
There exists a patch since many years, but this complicates the build process
and pulls with *libtiff* a lot of dependencies in.

Furthermore, *PIL* is unable to write fax compressed files, but blows the data
up to the full size, making this approach only a half solution as well.

After a longer odyssey I saw then the light of a Tiffany lamp:

I use only a hand-full of *PIL*s files, without any modification, pretend to unpack
a tiff file, but actually cheating. Only the tiff tags are nicely processed and
streamlined, but the compressed data is taken unmodified as-is.
When writing a tiff page out, the existing data is just assembled in the correct
order.

For many projects like *Pydica* that are processing tiff files without editing
their contents, this is a complete solution of their tiff problem. The dependencies
of the project stay minimal, there are no binaries required, and Tiffany is with
less than 300 lines remarkably small.

Because just 5 files from *PIL* are used and the _imaging module is not compiled
at all, I'm talking about "PIL without PIL" ;-)

Tiffany is a stand-alone module and has no interference with *PIL*.
You can see this by looking at ``import_mapper.py``. This module modifies ``__import__``
so that the *PIL* modules appear as top-level internally, but become sub-modules of
tiffany in ``sys.modules``.

Please let me know if this stuff works for you, and send requests to
<tismer@stackless.com> or use the links in the bitbucket website:

https://bitbucket.org/pydica/tiffany

easiest way to install tiffany:

    ``$ pip install tiffany``

# EOF


