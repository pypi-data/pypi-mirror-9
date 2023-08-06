# -*- coding: utf-8 -*-
"""Custom future.types.newstr stuff."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from future.types.newstr import newstr as str
from future import utils


__all__ = ['newstr']


class newstr(str):

    """Fix for :class:`~future.types.newstr.newstr`.

    This implements :meth:`isidentifier`, which currently raises a
    `NotImplementedError` in `future`.

    """

    def isidentifier(self):
        """Override to provide an actual implementation.

        This can be removed if the base ever includes the implementation or
        Python 2 support is removed.

        """
        return utils.isidentifier(self)
