# -*- coding: utf-8 -*-
"""The `pyneric.util` module contains generic utility functions."""

# Support Python 2 & 3.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pyneric.future import *

import keyword
import inspect
import re


__all__ = ['add_to_all']


def add_to_all(named_object):
    """Add the name of the given object to its module's *__all__* attribute.

    :param object named_object: anything with a *__name__* attribute
    :returns: *named_object* (unchanged)
    :raises TypeError: if the *__all__* attribute of `named_object`'s module is
                       not a `list`, `set`, or `tuple`

    This is meant to be used as a decorator for objects with a *__name__*
    attribute (such as functions and classes) defined in a module's global
    namespace.

    The applicable module is determined by passing *named_object* to
    :func:`inspect.getmodule`.  It is not recommended to pass an object that is
    not in the module's global namespace.  Passing an imported object attempts
    to add the name to the *__all__* attribute of the module in which the
    object was defined (also not recommended).

    """
    module = inspect.getmodule(named_object)
    all = module.__all__
    object_name = named_object.__name__
    if isinstance(all, list):
        all.append(object_name)
    elif isinstance(all, set):
        all.add(object_name)
    elif isinstance(all, tuple):
        module.__all__ += (object_name,)
    else:
        raise TypeError(
            "The type of __all__ ({}) in {} is unsupported."
            .format(type(all), module.__name__))
    return named_object


@add_to_all
def get_from_dict_or_objects(name, dict, objects, pop_from_dict=False):
    """Attempt to get a value via name from a mapping then from objects.

    :param str name: the name for which to look
    :param dict dict: the mapping in which to look first (by key)
    :param objects: the objects in which to look after *dict* (by attribute)
    :type objects: sequence of `object`\ s
    :param bool pop_from_dict: whether to :meth:`~dict.pop` rather than
                               :meth:`~dict.get` from *dict*
    :returns: the value found first
    :raises KeyError: if *dict* contains no such key and none of the *objects*
                      contain any such attribute

    """
    try:
        if pop_from_dict:
            return dict.pop(name)
        else:
            return dict[name]
    except KeyError as exc:
        for obj in objects:
            try:
                return getattr(obj, name)
            except AttributeError:
                pass
        raise exc


@add_to_all
def get_function_name(back=0):
    """Return the name of a function in the stack.

    By default (no arguments) the name of the caller of this function is
    returned, but the name of a function further back in the stack can be
    returned by specifying a positive integer indicating how many frames.

    :param int back: the number of frames beyond the caller to go back
    :raises IndexError: if `back` is too high for the stack

    """
    return inspect.stack()[1 + back][3]


@add_to_all
def module_attributes(module, use_all=None, include_underscored=False):
    """Return a set of the attribute names in the given module.

    :param module module: the module from which to get the attribute names
    :param bool use_all: whether to find attribute names from the module's
                         *__all__* attribute (`None` means only if it exists)
    :param bool include_underscored: whether to include attribute names that
                                     begin with an underscore when the
                                     *__all__* attribute is not used
    :rtype: `set`
    :raises AttributeError: if *use_all* is true and *module* has no *__all__*
                            attribute

    When the attribute names are not gotten from the module's *__all__*
    attribute, then the module is passed to :func:`dir` to get the names.

    Passing a true value for `use_all` is a convenience for the caller when it
    requires that the module shall have an *__all__* attribute and an exception
    shall be raised if it does not.

    """
    if use_all or use_all is None and hasattr(module, '__all__'):
        return set(module.__all__)
    result = set(dir(module))
    if include_underscored:
        return result
    return set(x for x in result if not x.startswith('_'))


@add_to_all
def pascalize(value, validate=True):
    """Return the conversion of the given string value to Pascal casing.

    :param str value: the string to convert
    :param bool validate: whether to also validate that *value* is a valid
                          Python identifier
    :rtype: `str`
    :raises TypeError: if *value* is not a string
    :raises ValueError: if *validate* is true and *value* fails validation

    This converts lower-case characters preceded by an underscore to upper-case
    without the underscore.

    """
    if validate:
        valid_python_identifier(value, exception=True)
    elif not isinstance(value, basestring):  # pragma: no cover
        raise TypeError("{!r} is not a string.".format(value))
    result_type = type(value)
    result = re.sub('(?:^|_)(.)', lambda x: x.group(0)[-1].upper(), value)
    if type(result) is not result_type:  # pragma: no cover
        result = result_type(result)
    return result


@add_to_all
def raise_attribute_error(obj, attr):
    """Raise an instance of `AttributeError` with the standard message.

    :param object obj: the object that is said to not have the attribute
    :param str attr: the attribute that *object* does not have
    :raises AttributeError:

    """
    what = ("type object {!r}".format(obj.__name__)
            if isinstance(obj, type) else
            "{!r} object").format(type(obj).__name__)
    raise AttributeError("{} has no attribute {!r}".format(what, attr))


@add_to_all
# PY2 note: The definition would be the following in Python 3+:
# def tryf(func, *args, _except=Exception, _return=None, **kwargs):
def tryf(func, *args, **kwargs):
    """Wrap a function call in a try/except statement.

    :param function func: the function to call
    :param args: the positional arguments to pass to *func*
    :param kwargs: the keyword arguments to pass to *func*
    :param _except: the exception(s) to catch
    :type _except: `BaseException` or sequence of such
    :param _return: the value to return if calling *func* raises *_except*

    If *func* expects keyword arguments named '_except' or '_return', it will
    never receive them, so the try statement should be used for those instead
    of this function.

    """
    # PY2 note: The _except and _return assignments should be removed when the
    # function definition changes to Python 3+ syntax.
    _except = kwargs.pop('_except', Exception)
    _return = kwargs.pop('_return', None)
    try:
        return func(*args, **kwargs)
    except _except:
        return _return


@add_to_all
def underscore(value, validate=True, multicap=True):
    """Return the conversion of the given string value to variable casing.

    :param str value: the string to convert
    :param bool validate: whether to also validate that *value* is a valid
                          Python identifier
    :param bool multicap: a directive to make consecutive upper-case characters
                          one word (only one initial underscore) until an upper
                          followed by lower is encountered
    :rtype: `str`
    :raises TypeError: if *value* is not a string
    :raises ValueError: if *validate* is true and *value* fails validation

    This converts upper-case characters to lower-case preceded by an underscore
    unless it is the first character.

    *multicap* example:

    >>> underscore('ABCDefGHijKLMNOPqrs')  # multicap=True is default
    'abc_def_g_hij_klmno_pqrs'

    >>> underscore('ABCDefGHijKLMNOPqrs', multicap=False)
    'a_b_c_def_g_hij_k_l_m_n_o_pqrs'

    """
    if validate:
        valid_python_identifier(value, exception=True)
    elif not isinstance(value, basestring):  # pragma: no cover
        raise TypeError("{!r} is not a string.".format(value))
    patterns = ['[A-Z]']
    if multicap:
        patterns.insert(0, '[A-Z]+(?=($|[A-Z][a-z]))')
    pattern = '(' + '|'.join(patterns) + ')'
    result = re.sub(pattern, lambda x: "_" + x.groups()[0].lower(), value)[1:]
    result_type = type(value)
    if type(result) is not result_type:  # pragma: no cover
        result = result_type(result)
    return result


@add_to_all
def valid_python_identifier(value, dotted=False, exception=False):
    """Validate that the given string value is a valid Python identifier.

    :param str value: the identifier to validate
    :param bool dotted: if true, then each string around any dots is validated
    :param exception: whether to raise an exception (see raises)
    :type exception: `bool` or `BaseException`
    :returns: whether *value* is a valid non-keyword Python identifier
    :rtype: `bool`
    :raises *exception*: if it is an exception class and validation fails
    :raises ValueError: if *exception* is true and validation fails

    """
    if not isinstance(value, basestring):
        raise TypeError("{!r} is not a string.".format(value))
    if dotted:
        return all(valid_python_identifier(x, exception=exception)
                   for x in value.split('.'))
    problem = None
    if not future.isidentifier(value, dotted=dotted):
        problem = "is not a valid Python identifier"
    elif keyword.iskeyword(value):
        problem = "is a Python keyword"
    if not (problem and exception):
        return not problem
    if not (inspect.isclass(exception) and
            issubclass(exception, BaseException)):
        exception = ValueError
    raise exception("{!r} {}.".format(value, problem))
