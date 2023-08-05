The pyneric package provides generic Python utilities and extensions.

The `source <https://github.com/gnuworldman/pyneric/tree/master>`_,
`documentation <http://gnuworldman.github.io/pyneric/>`_,
and `issues <https://github.com/gnuworldman/pyneric/issues>`_
are hosted on `GitHub <https://github.com/>`_.

This is an open-source project by and for the community.  Contributions,
suggestions, and questions are `welcome <https://twitter.com/BraveGnuWorld>`_
(Twitter: @bravegnuworld).

.. image:: https://travis-ci.org/gnuworldman/pyneric.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/gnuworldman/pyneric

.. image:: https://img.shields.io/coveralls/gnuworldman/pyneric.svg
   :alt: Coverage Status
   :target: https://coveralls.io/r/gnuworldman/pyneric?branch=master

Overview
========

This library is intended as a place for Python code whose scope is generic, not
specific to any particular business domain.  The pyneric.future package is
intended to include everything needed to easily support Python 2.7 and 3.3+
simultaneously using the Python-Future library.

Examples
========

Importing
---------

>>> import pyneric

Supporting recent versions Python 2 and 3 simultaneously
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The `future` package does a great job of allowing one to support Python 2.6,
2.7, and 3.3+ with the same code base; however, some modifications that exist
in the `pyneric.future` package can help ease or fix a few shortcomings.  One
can use the following to import common 2/3 compatibility features::

 from __future__ import absolute_import, division, print_function, unicode_literals
 from pyneric.future import *

Python identifier transformation
--------------------------------

lower/underscore to titled-terms (pascalize function)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> pyneric.pascalize('basic_python_identifier')
'BasicPythonIdentifier'

titled-terms to lower/underscore (underscore function)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> pyneric.underscore('BasicPythonIdentifier')
'basic_python_identifier'

Get a function name from the stack
----------------------------------

the current function name
^^^^^^^^^^^^^^^^^^^^^^^^^
>>> def foo():
...     return pyneric.get_function_name()
...
>>> foo()
'foo'

also further back in the stack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
>>> def foo():
...     def bar():
...         return pyneric.get_function_name(1) + pyneric.get_function_name()
...     return bar()
...
>>> foo()
'foobar'

Return upon exception (tryf function)
-------------------------------------

no exception
^^^^^^^^^^^^

>>> pyneric.tryf(tuple, [])
()

catch any non-system-exiting exception by default
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> pyneric.tryf(tuple, object)


catch more specific exceptions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
>>> pyneric.tryf(tuple, object, _except=TypeError)


return a different value upon exception
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
>>> pyneric.tryf(tuple, object, _return=())
()

Test Python identifier validity
-------------------------------

return boolean
^^^^^^^^^^^^^^

>>> pyneric.valid_python_identifier('not_a_keyword')
True
>>> pyneric.valid_python_identifier('class')
False
>>> pyneric.valid_python_identifier('xyz.abc', dotted=True)
True
>>> pyneric.valid_python_identifier('class.keyword', dotted=True)
False

raise exception
^^^^^^^^^^^^^^^

>>> pyneric.valid_python_identifier('not_a_keyword', exception=True)
True
>>> pyneric.valid_python_identifier('class', exception=True)
Traceback (most recent call last):
  ...
ValueError: 'class' is a Python keyword.

raise a specific exception
^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> class MyException(Exception): pass

>>> pyneric.valid_python_identifier('1nv4l1d', exception=MyException)
Traceback (most recent call last):
  ...
MyException: '1nv4l1d' is not a valid Python identifier.

Make a request to a REST resource
---------------------------------

>>> class UserAgent(pyneric.rest_requests.RestResource): url_path = 'user-agent'

>>> headers = {'User-Agent': 'Mozilla, but not really', 'Accept': 'application/json'}

>>> str(UserAgent('http://httpbin.org').get(headers=headers).json()['user-agent'])
'Mozilla, but not really'
