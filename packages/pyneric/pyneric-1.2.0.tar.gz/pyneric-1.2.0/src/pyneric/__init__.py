# -*- coding: utf-8 -*-
"""The `pyneric` package contains Python helpers and utility functions.

For convenience, many of the library's components are imported by the
pyneric package's __init__ module so that they may be accessed directly under
pyneric, such as:

* `~pyneric.meta.Metaclass`
* `~pyneric.rest_requests.RestResource`
* `~pyneric.util.tryf`

Components (in modules/subpackages) that require extra dependencies should not
be imported here.  For example `pyneric.fsnotify` depends on `pyinotify`, so
`~pyneric.fsnotify.FileSystemNotifier` must be imported from that module. If it
was imported here, then the library would need to unconditionally require
`pyinotify`, which is not desired.

"""

# flake8: noqa

from ._version import __version__, __version_info__
# from .fsnotify import *  # has extra dependencies
from .meta import *
from .rest_requests import *
from .util import *
