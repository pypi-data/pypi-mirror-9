import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "tiffany",
    version = "0.6.7",
    author = "Christian Tismer",
    author_email = "tismer@stackless.com",
    description = ("Tiffany -- read/write/arrange any multi-page Tiff, any compression"),
    license = "PSF",
    keywords = "tiff fax G3/G4 multi-page monkeypatch PIL pydica",
    url = "https://bitbucket.org/pydica/tiffany",
    download_url = "https://bitbucket.org/pydica/tiffany/downloads",
    test_suite = 'tiffany.test_tiffany',
    packages=['tiffany'],
    long_description=read('README.rst'),
    # note that this _must_ be README or README.txt :-(
    # unless you use a MANIFEST.in file :-)
    classifiers = [f.strip() for f in """
        Programming Language :: Python
        Programming Language :: Python :: 2.6
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3.2
        Programming Language :: Python :: 3.3
        Programming Language :: Python :: 3.4
        Development Status :: 5 - Production/Stable
        Environment :: X11 Applications :: Qt
        Environment :: Console
        Environment :: MacOS X
        Environment :: Win32 (MS Windows)
        Environment :: Other Environment
        License :: OSI Approved :: Python Software Foundation License
        Intended Audience :: End Users/Desktop
        Intended Audience :: Developers
        Natural Language :: English
        Topic :: Multimedia :: Graphics :: Capture :: Scanners
        Topic :: Multimedia :: Graphics :: Graphics Conversion
        Topic :: Other/Nonlisted Topic
        Topic :: Software Development :: Libraries :: Python Modules
        Topic :: Utilities
    """.splitlines() if f.strip()],
    include_package_data = True,
    zip_safe = False,
    install_requires = [
        #'distribute',
        # -*- Extra requirements: -*-
    ],
    entry_points = '\n'.join(f.strip() for f in """
    # -*- Entry points: -*-
    """.splitlines() if f.strip()),
    )
