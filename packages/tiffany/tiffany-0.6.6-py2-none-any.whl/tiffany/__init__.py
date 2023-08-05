import os
import sys

__path__[0] = os.path.realpath(__path__[0])
__file__ = os.path.realpath(__file__)

__author__ = "Christian Tismer <tismer@stackless.com>"
__version__ = "0.6.6"

def start_mapper():
    from tiffany.import_mapper import install_mapper, mapped_dir
    __path__.append(mapped_dir)
    install_mapper()
    import tiffany.compat


def stop_mapper():
    from tiffany.import_mapper import uninstall_mapper
    __path__[1:] = []
    uninstall_mapper()

start_mapper()
from tiffany.monkeypil import open
stop_mapper()

__all__ = ['open']
