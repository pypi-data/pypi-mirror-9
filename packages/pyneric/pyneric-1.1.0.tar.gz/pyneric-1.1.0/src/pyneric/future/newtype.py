# -*- coding: utf-8 -*-
"""Custom builtin type stuff."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from pyneric.future.newsuper import newsuper as super
from future import utils


__all__ = ['newtype']


class newtype(type):

    """Future support for :class:`type` in Python 2.

    This forces `name` and the dictionary keys to the native str type.

    """

    def __new__(cls, *args, **kwargs):
        if (len(args) == 1 and not kwargs or
            not args and list(kwargs.keys()) == ['object']):
            return super().__new__(cls, *args, **kwargs)
        name = kwargs.get('name', args[0])
        bases = kwargs.get('bases', args[1])
        dct = kwargs.get('dict', args[2])
        name = utils.native_str(name)
        dct = dict((utils.native_str(x), y) for x, y in dct.items())
        return super().__new__(cls, name, bases, dct)
