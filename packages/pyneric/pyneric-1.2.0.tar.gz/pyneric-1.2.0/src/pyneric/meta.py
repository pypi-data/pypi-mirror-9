# -*- coding: utf-8 -*-
"""The `pyneric.meta` module contains helpers for metaclassing."""

# Support Python 2 & 3.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pyneric.future import *

import collections
from copy import copy
import inspect

from pyneric import util


__all__ = []

METADATA_BEHAVIOUR_ATTRIBUTE = '__metadata_behaviour__'
"""The `Metaclass` class attribute storing the `MetadataBehaviour` instance."""


@util.add_to_all
class MetadataBehaviour(object):

    """The behaviour of a `Metaclass`.

    This behaviour defines how the metadata in a `Metaclass` is defined and
    managed.  The default behaviour should work for most needs unless there are
    conflicting attributes or methods.  Another reason to use non-default
    behaviour would be to apply `Metaclass` to an existing metadata management
    paradigm.

    """

    def __init__(self, metadata_attr='__metadata__',
                 propagate_attr='__propagate__',
                 base_override_attr='__base_overrides__',
                 validate_prefix='validate_',
                 storage_attr='__metadata__',
                 storage_class=dict,
                 metadata_getter='_get_metadata',
                 validate_transforms=False):
        # Validate arguments so that issues are caught early.
        attr_dict = dict(metadata_attr=metadata_attr,
                         propagate_attr=propagate_attr,
                         base_override_attr=base_override_attr,
                         validate_prefix=validate_prefix,
                         storage_attr=storage_attr,
                         metadata_getter=metadata_getter)
        for name, value in attr_dict.items():
            required = name in ('metadata_attr', 'storage_attr',
                                'metadata_getter')
            if not (value is None and not required or
                    isinstance(value, basestring)):
                raise TypeError(
                    "{} must be a string{}."
                    .format(name, "" if required else " or None"))
        if not inspect.isclass(storage_class):
            raise TypeError("storage_class must be a class.")

        self._metadata_attr = metadata_attr
        self._propagate_attr = propagate_attr
        self._base_override_attr = base_override_attr
        self._validate_prefix = validate_prefix
        self._storage_attr = storage_attr
        self._storage_class = storage_class
        self._metadata_getter = metadata_getter
        self._validate_transforms = validate_transforms

    @property
    def metadata_attr(self):
        """The name of a class attribute that may contain metadata.

        The attribute may be a sequence of attribute names or a mapping of
        metadata values keyed by attribute name.  The attribute names become
        identifiers of user metadata, as opposed to internally managed metadata
        such as :attr:`propagate_attr` and :attr:`storage_attr`.

        """
        return self._metadata_attr

    @property
    def propagate_attr(self):
        """The attribute name that contains the propagated attribute names.

        This is the name of an internally-managed metadata attribute that can
        be used to specify which user metadata attributes are also accessible
        from an instance of the metaclass.

        If this is `None`, then no propagation occurs.

        """

        return self._propagate_attr

    @property
    def base_override_attr(self):
        """The attribute name that contains a mapping of overridden values.

        This is the name of an internally-managed metadata attribute that can
        be used to specify user metadata values that should override values
        obtained from base metaclasses.  If the metadata value is specified
        directly in the derived metaclass, then this has no effect.

        If this is `None`, then no metadata from bases are overridden.

        """
        return self._base_override_attr

    @property
    def storage_attr(self):
        """The name of the attribute in which metadata is stored.

        This is the name of a metadata behaviour attribute that is used to
        store the metadata in the metaclass.

        This value is required because the metadata must be stored and accessed
        from somewhere.

        """
        return self._storage_attr

    @property
    def storage_class(self):
        """The class used to contain metadata.

        The class specified must be able to accept user metadata arguments via
        its constructor and provide access to metadata values.  If this is not
        a `~collections.Mapping`, then the metadata values must be accessible
        as attributes.

        This value is required because the metadata must be stored and accessed
        somehow.

        """
        return self._storage_class

    @property
    def metadata_getter(self):
        """The name of the class method used to retrieve metadata values.

        This applies to both `Metaclass` instances and classes built with them.

        """
        return self._metadata_getter

    @property
    def storage_is_mapping(self):
        """Return whether the `storage_class` is a `~collections.Mapping`."""
        return issubclass(self._storage_class, collections.Mapping)

    def define_property_if_not_descriptor(self, dict, attr):
        """Define a property in `dict` if it is not already a data descriptor.

        :param dict dict: The mapping in which to define the property.
        :param str attr: The key in the mapping to which to set the property.

        """
        try:
            value = dict[attr]
        except KeyError:
            pass
        else:
            if inspect.isdatadescriptor(value):
                return
        dict[attr] = property(lambda self, attr=attr, behaviour=self:
                              getattr(self, behaviour._metadata_getter)(attr)
                              if isinstance(type(self), _Metametaclass) else
                              getattr(type(self), attr))

    def _get_local_metadata(self, dict, base_attrs=()):
        result = {}
        metadata = dict.pop(self._metadata_attr, {})
        if isinstance(metadata, collections.Mapping):
            result.update(metadata)
        elif not isinstance(metadata, collections.Iterable):
            raise TypeError(
                "The '{}' attribute must be a mapping or iterable."
                .format(self._metadata_attr))
        for attr in tuple(metadata) + tuple(base_attrs):
            try:
                value = dict[attr]
            except KeyError:
                continue
            if not inspect.isdatadescriptor(value):
                result[attr] = value
        return result

    def get_behavioural_data(self, cls):
        """Return a three-tuple containing a class's behavioural data.

        :param cls: The class from which to get the behavioural data.
        :returns: Three-tuple whose elements are metadata, propagated
                  attributes, and base-override attributes.
        :rtype: tuple

        """
        metadata = getattr(cls, self._storage_attr)
        if not issubclass(self._storage_class, collections.Mapping):
            metadata = metadata.__dict__
        metadata = metadata.copy()
        propagate = (set(metadata.pop(self._propagate_attr, ()))
                     if self._propagate_attr else None)
        base_overrides = (dict(metadata.pop(self._base_override_attr, {}))
                          if self._base_override_attr else None)
        return metadata, propagate, base_overrides

    def get_class_metadata(self, cls, bases, dict):
        """Return the metadata defined in a class definition.

        :param class cls: The class being defined.
        :param tuple bases: The base classes from the class definition.
        :param dict dict: The attribute dictionary from the class definition.
        :returns: All (user and internally-managed) metadata from the class
                  (including those inherited from applicable base metaclasses)
        :rtype: dict

        """
        result = {}
        propagate = set(dict.pop(self._propagate_attr, ()))
        base_overrides = dict.pop(self._base_override_attr, {}).copy()
        if isinstance(cls, _Metametaclass):
            behaviour = getattr(cls, METADATA_BEHAVIOUR_ATTRIBUTE)
            m, p, b = behaviour.get_behavioural_data(cls)
            result.update(m)
            if p:
                propagate |= p
            if b:
                base_overrides.update(x for x in b.items()
                                      if x[0] not in base_overrides)
        if issubclass(cls, _Metametaclass):
            metabases = [x for x in bases if isinstance(x, _Metametaclass)]
            if metabases:
                for base in reversed(metabases):
                    m, p, b = base.behavioural_data
                    result.update(m)
                    if p:
                        propagate |= p
                    if b:
                        base_overrides.update(b)
        for attr, value in base_overrides.items():
            result[attr] = value
        result.update(self._get_local_metadata(dict, tuple(result)))
        if self._propagate_attr:
            propagate |= set(result.get(self._propagate_attr, ()))
            result[self._propagate_attr] = propagate
        if self._base_override_attr:
            base_overrides.update(result.get(self._base_override_attr, {}))
            result[self._base_override_attr] = base_overrides
        return result

    def get_metadata(self, cls, attr=None):
        """Return metadata from the given class.

        :param class cls: The class from which to retrieve metadata.
        :param attr: The attribute identifying which metadata to return.
        :type attr: str or None
        :returns: A shallow copy of all metadata if `attr` is `None`;
                  otherwise, the metadata value identified by `attr`.

        """
        metadata = getattr(cls, self._storage_attr)
        if not attr:
            return copy(metadata)
        if not self.storage_is_mapping:
            return getattr(metadata, attr)
        try:
            return metadata[attr]
        except KeyError:
            pass
        util.raise_attribute_error(cls, attr)

    def prepare_new(self, cls, bases, dict):
        """Prepare `dict` prior to calling :meth:`~type.__new__`.

        This sets values in `dict` that must be set during class creation to
        manage the metadata properly.

        """
        metadata = self.get_class_metadata(cls, bases, dict)
        if self._validate_prefix:
            for attr, value in metadata.items():
                try:
                    validate = getattr(cls, self._validate_prefix + attr)
                except AttributeError:
                    continue
                if not callable(validate):
                    continue
                new_value = validate(value)
                if self._validate_transforms and new_value != value:
                    metadata[attr] = new_value
        if self._propagate_attr:
            for attr in metadata[self._propagate_attr]:
                self.define_property_if_not_descriptor(dict, attr)
        dict[self._storage_attr] = self._storage_class(**metadata)
        dict[self._metadata_getter] = classmethod(
            lambda c, attr=None:
            getattr(c, METADATA_BEHAVIOUR_ATTRIBUTE).get_metadata(c, attr))


class _Metametaclass(type):

    def __new__(cls, name, bases, dict):
        behaviour = util.get_from_dict_or_objects(METADATA_BEHAVIOUR_ATTRIBUTE,
                                                  dict, bases)
        metadata = behaviour.get_class_metadata(cls, bases, dict)
        for attr in metadata:
            behaviour.define_property_if_not_descriptor(dict, attr)
        dict[behaviour.storage_attr] = behaviour.storage_class(**metadata)
        dict[behaviour.metadata_getter] = classmethod(
            lambda c, attr=None:
            getattr(c, METADATA_BEHAVIOUR_ATTRIBUTE).get_metadata(c, attr))
        new_class = super().__new__(cls, name, bases, dict)
        return new_class

    @property
    def behavioural_data(self):
        """Return a tuple containing this class's behavioural data.

        See :meth:`MetadataBehaviour.get_behavioural_data` for details.

        """
        behaviour = getattr(self, METADATA_BEHAVIOUR_ATTRIBUTE)
        return behaviour.get_behavioural_data(self)


@util.add_to_all
class Metaclass(future.with_metaclass(_Metametaclass, type)):

    """A metaclass for managing metadata.

    Metadata management can be customized by specifying a different
    `MetadataBehaviour` instance in the `__metadata_behaviour__` attribute.

    The following applies when default metadata behaviour is used.  Metadata
    may be defined with in the :attr:`__metadata__` attribute in the metaclass
    definition, which may be an iterable of attribute names or a mapping of
    values keys by attribute name.  These defined metadata attributes can be
    set via attributes in the class definition and accessed via class
    attributes.  Metadata may be propagated (as properties) to instances by
    specifying their attribute names in the :attr:`__propagate__` attribute
    when access to metadata from the class's instances is desired.  The
    :attr:`__base_overrides__` attribute may be set to a mapping of metadata
    values keyed by attribute name to automatically set those metadata values
    in derived metaclasses when it has not defined the metadata value itself.

    """

    __metadata_behaviour__ = MetadataBehaviour()
    """See :class:`MetadataBehaviour`."""

    def __new__(cls, name, bases, dict):
        behaviour = getattr(cls, METADATA_BEHAVIOUR_ATTRIBUTE)
        behaviour.prepare_new(cls, bases, dict)
        return super(Metaclass, cls).__new__(cls, name, bases, dict)
