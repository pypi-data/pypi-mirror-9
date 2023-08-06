# -*- coding: utf-8 -*-
"""The `pyneric.fsnotify` module contains file system notification helpers.

Use of this module requires the
`pyinotify <https://pypi.python.org/pypi/pyinotify>`_ library.

"""

# Support Python 2 & 3.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pyneric.future import *

try:
    import pyinotify
except ImportError:  # pragma: no cover
    raise ImportError("The pyneric.fsnotify module requires pyinotify.")

# Check the pyinotify version (must be >= 0.9).
_version = pyinotify.__version__.split('.')
if not (int(_version[0]) > 0 or int(_version[1]) >= 9):  # pragma: no cover
    raise ImportError("The pyneric.fsnotify module requires pyinotify >= 0.9.")
del _version

from pyneric.util import add_to_all, raise_attribute_error


__all__ = []


@add_to_all
class FileSystemNotifier(object):

    """Notify the caller of file system changes via a queue using pyinotify.

    Events from the pyinotify library are put onto the queue according to the
    watches the caller configures in `watch_manager`.  The notifier needs to be
    started via :meth:`start` to get the events.  The notifier needs to be
    stopped via :meth:`stop` when the caller would like to stop the events or
    delete the notifier.

    Note that the inotify polling occurs in a separate thread, and one such
    thread is created for each `FileSystemNotifier` instance, so if it is
    feasible, sharing a notifier/queue is recommended for multiple watches.

    .. _pyinotify.ThreadedNotifier:
       http://seb-m.github.io/pyinotify/pyinotify.ThreadedNotifier-class.html

    .. _pyinotify.ThreadedNotifier.stop():
       http://seb-m.github.io/pyinotify/pyinotify.ThreadedNotifier-class.html#stop

    .. _pyinotify.WatchManager:
       http://seb-m.github.io/pyinotify/pyinotify.WatchManager-class.html

    .. py:attribute:: notifier

       A `pyinotify.ThreadedNotifier`_ instance that is a Python
       `~threading.Thread` that watches the file system for events configured
       in `watch_manager`.  Those events are put on the `queue` as they occur.

    .. py:attribute:: queue

       A Python `queue.Queue` instance (or `Queue.Queue` in Python 2) that is
       provided to the constructor.

    .. py:attribute:: watch_manager

       A `pyinotify.WatchManager`_ instance that provides management for which
       events to watch on which files and directories.

    .. py:method:: start

       See :meth:`threading.Thread.start`.

    .. py:method:: stop

       See `pyinotify.ThreadedNotifier.stop()`_.

    All other methods are passed through to `watch_manager`.  See
    `pyinotify.WatchManager`_.

    """

    def __init__(self, queue):
        def process_func(self, event):
            queue.put(event)
        self.queue = queue
        ProcessEvent = type('ProcessEvent', (pyinotify.ProcessEvent,),
                            dict(process_default=process_func))
        self.watch_manager = pyinotify.WatchManager()
        self.notifier = pyinotify.ThreadedNotifier(self.watch_manager,
                                                   ProcessEvent())

    def __getattr__(self, item):
        proxy_for = self.watch_manager
        if item in ('start', 'stop'):
            proxy_for = self.notifier
        try:
            return getattr(proxy_for, item)
        except AttributeError:
            raise_attribute_error(self, item)
