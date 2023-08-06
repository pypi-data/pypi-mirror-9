# -*- coding: utf-8 -*-
"""pyneric.future module

This is equivalent to future.builtins with additions and customizations.

"""
# flake8: noqa

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from future.builtins import *
from future.builtins import __all__ as _all


_all = set(_all)

_all.add('future')
from future import utils as future

# PY2 note: Remove the basestring import and replace 'basestring' with 'str' in
# code when removing Python 2 support.
_all.add('basestring')
from past.builtins import basestring

if future.PY2:
    _all |= {'str', 'super', 'type'}
    from pyneric.future.newstr import newstr as str
    from pyneric.future.newsuper import newsuper as super
    from pyneric.future.newtype import newtype as type


_all.add('python_2_unicode_compatible')
def python_2_unicode_compatible(cls):
    cls = future.python_2_unicode_compatible(cls)
    if future.PY2:
        cls.__str__ = lambda self: unicode(self.__unicode__()).encode()
    return cls
python_2_unicode_compatible.__doc__ = future.python_2_unicode_compatible.__doc__

__all__ = list(future.native_str(x) for x in _all)
