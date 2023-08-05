# -*- coding: utf-8 -*-
"""
============================
myscipkg3
============================
"""
import pkg_resources

# Get __version__ from setup.py version number
# See https://github.com/hgrecco/pint/blob/master/pint/__init__.py
try:
    __version__ = pkg_resources.get_distribution('pint').version
except:
    # we seem to have a local copy installed without setuptools
    # so the reported version will be unknown
    __version__ = "unknown"

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
