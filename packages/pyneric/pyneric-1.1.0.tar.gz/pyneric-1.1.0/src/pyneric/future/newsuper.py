# -*- coding: utf-8 -*-
"""Custom future.builtins.newsuper stuff."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import sys
from types import FunctionType


__all__ = ['newsuper']

_builtin_super = super

_SENTINEL = object()


def newsuper(typ=_SENTINEL, type_or_obj=_SENTINEL, framedepth=1):
    """Fix for :meth:`~future.builtins.newsuper.newsuper`.

    See the '*** CUSTOMIZATION ***' block below.

    """
    #  Infer the correct call if used without arguments.
    if typ is _SENTINEL:  # pragma: no branch
        # We'll need to do some frame hacking.
        f = sys._getframe(framedepth)

        try:
            # Get the function's first positional argument.
            type_or_obj = f.f_locals[f.f_code.co_varnames[0]]
        except (IndexError, KeyError,):  # pragma: no cover
            raise RuntimeError('super() used in a function with no args')

        try:
            # Get the MRO so we can crawl it.
            mro = type_or_obj.__mro__
        except AttributeError:
            try:
                mro = type_or_obj.__class__.__mro__
            except AttributeError:  # pragma: no cover
                raise RuntimeError('super() used with a non-newstyle class')

        #   A ``for...else`` block?  Yes!  It's odd, but useful.
        #   If unfamiliar with for...else, see:
        #
        #       http://psung.blogspot.com/2007/12/for-else-in-python.html
        for typ in mro:
            #  Find the class that owns the currently-executing method.
            for meth in typ.__dict__.values():
                # *** CUSTOMIZATION ***
                # We must not drill down into properties due to side effects.
                if isinstance(meth, property):
                    continue
                # *** END CUSTOMIZATION ***
                # Drill down through any wrappers to the underlying func.
                # This handles e.g. classmethod() and staticmethod().
                try:
                    while not isinstance(meth, FunctionType):
                        try:
                            meth = meth.__func__
                        except AttributeError:
                            meth = meth.__get__(type_or_obj)
                except (AttributeError, TypeError):
                    continue
                if meth.func_code is f.f_code:
                    break   # Aha!  Found you.
            else:
                continue    # Not found! Move onto the next class in MRO.
            break    # Found! Break out of the search loop.
        else:  # pragma: no cover
            raise RuntimeError('super() called outside a method')

    #  Dispatch to builtin super().
    if type_or_obj is not _SENTINEL:
        return _builtin_super(typ, type_or_obj)
    return _builtin_super(typ)  # pragma: no cover
