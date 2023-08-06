# -*- coding: utf-8 -*-
"""The `pyneric.rest_requests` module contains REST resource classes."""

# Support Python 2 & 3.
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from pyneric.future import *
from future.standard_library import install_aliases
install_aliases()

import inspect
import functools
from urllib.parse import urljoin, urlsplit, urlunsplit

from pyneric.meta import Metaclass
from pyneric.util import tryf
from pyneric import util


__all__ = []


def _url_split(url):
    result = list(urlsplit(url))
    result[2] = result[2].rstrip('/')
    result[3:] = '', ''
    return result


def _with_trailing_slash(value):
    if not value.endswith('/'):
        value += '/'
    return value


class _RestMetaclass(Metaclass):

    __metadata__ = dict(url_path=None, container_class=None,
                        container_is_collection=False,
                        reference_attribute=None)
    __propagate__ = tuple(__metadata__) + ('is_abstract',)

    @staticmethod
    def validate_url_path(value):
        if not (value is None or
                isinstance(value, basestring) and value):
            raise TypeError(
                "invalid url_path attribute: {!r}"
                .format(value))

    @staticmethod
    def validate_container_class(value):
        if not (value is None or
                inspect.isclass(value) and
                issubclass(value, RestResource)):
            raise TypeError(
                "invalid container_class attribute: {!r}"
                .format(value))

    @staticmethod
    def validate_reference_attribute(value):
        if value is not None:
            if not isinstance(value, basestring):
                raise TypeError(
                    "invalid reference_attribute attribute: {!r}"
                    .format(value))
            try:
                util.valid_python_identifier(value, exception=ValueError)
            except ValueError as exc:
                raise ValueError(
                    "invalid reference_attribute attribute: {}"
                    .format(exc))

    @property
    def is_abstract(cls):
        """Return whether this resource class is abstract (no url_path)."""
        return cls.url_path is None


@util.add_to_all
class RestResource(future.with_metaclass(_RestMetaclass, object)):

    """A standard REST resource.

    A REST resource is represented by a (usually HTTP) URL, which is specified
    in this class via the combination of the `container` passed to the
    constructor and the :attr:`url_path`.  See the attribute documentation for
    more details.

    """

    url_path = None
    """Path segment(s) identifying the REST resource.

    This may be `None` to signify that this is an abstract resource; otherwise,
    it is the path under the base (API root or containing resource) identifying
    this resource.

    This should not start or end with a path separator ("/"), but it may
    contain separator(s) if there is no need to access the path segment(s)
    before the last separator as distinct REST resource(s).

    """

    container_class = None
    """The parent REST resource that contains this resource.

    The `container` passed to the constructor must be an instance of this
    resource.  If this is `None`, then the `container` passed to the
    constructor must be a URL string under which this resource resides.

    An attribute named after this class or explicitly named by this class is
    created to reference the instance passed to the constructor as `container`.

    """

    container_is_collection = False
    """Whether the containing resource is the specified collection.

    This only applies when the :attr:`container_class` is a subclass of
    `RestCollection`; it is simply a convenience for automatically confirming
    the resource's validity within the REST API.

    If this is false, then this resource exists under each member of the
    collection; otherwise, it exists directly under the collection itself.

    """

    reference_attribute = None
    """The attribute name used to refer to this resource.

    For example, this applies when another resource refers to this one as the
    container.

    If this is `None` (the default), then the attribute used to refer to this
    resource (as container) is the class name converted to lower-case and
    underscored (with additional underscore(s) appended when it would conflict
    with existing attributes in the referring resource).

    """

    def __init__(self, container):
        def invalid_for_type():
            raise ValueError(
                "Container {!r} is invalid for resource type {!r}."
                .format(container, type(self)))
        if self.is_abstract:
            raise TypeError("abstract RestResource is uninstantiable")
        self._container = container
        if self.container_class:
            if not (isinstance(container, self.container_class) and
                    (not issubclass(self.container_class, RestCollection) or
                     self.container_is_collection is None or
                     bool(self.container_is_collection) is
                     (container.id is None))):
                invalid_for_type()
            attr = self.container_class.reference_attribute
            if not attr:
                attr = util.underscore(self.container_class.__name__)
                while hasattr(self, attr):
                    attr += '_'
            setattr(self, attr, container)
            container = container.url
        elif not isinstance(container, basestring):
            invalid_for_type()
        self._url = urljoin(_with_trailing_slash(container), self.url_path)

    @classmethod
    def from_url(cls, url):
        """Construct an instance of this resource based on the given URL."""
        try:
            return cls._from_url(url)
        except Exception as exc:
            raise ValueError(
                "The URL {!r} is invalid for {}.  {}"
                .format(url, cls.__name__, exc))

    @classmethod
    def _from_url(cls, url, **kwargs):
        container = cls._get_container_from_url(url)
        if cls.container_class:
            container = cls.container_class.from_url(container)
        return cls(container, **kwargs)

    @classmethod
    def _get_container_from_url(cls, url):
        url_split = _url_split(url)
        segments = url_split[2].split('/')
        resource_segments = cls.url_path.split('/')
        size = len(resource_segments)
        if segments[-size:] != resource_segments:
            multiple = size != 1
            raise ValueError(
                "The last {}segment{} of the URL {!r} {} invalid for {}."
                .format("{} ".format(size) if multiple else "",
                        "s" if multiple else "", url,
                        "are" if multiple else "is", cls.__name__))
        url_split[2] = '/'.join(segments[:-size])
        return urlunsplit(url_split)

    def __getattr__(self, item):
        try:
            import requests
        except ImportError:  # pragma: no cover
            pass
        else:
            try:
                func = getattr(requests, item)
            except AttributeError:
                pass
            else:
                if (inspect.isfunction(func) and
                    'url' in (inspect.getargspec(func).args if future.PY2 else
                              inspect.signature(func).parameters)):
                    return functools.partial(func, url=self.url)
        util.raise_attribute_error(self, item)

    @property
    def container(self):
        """The container of this resource.

        This is an instance of :attr:`container_class` if that is not `None`;
        otherwise, this is the REST URL under which this resource resides.

        """
        return self._container

    @property
    def url(self):
        """The complete URL of the resource."""
        return self._url


class _RestCollectionMetaclass(_RestMetaclass):

    __metadata__ = dict(id_type=str)
    __propagate__ = tuple(__metadata__)

    @classmethod
    def validate_id_type(cls, value):
        if not inspect.isclass(value):
            raise TypeError(
                "invalid id_type attribute: {!r}"
                .format(value))


@util.add_to_all
class RestCollection(future.with_metaclass(_RestCollectionMetaclass,
                                           RestResource)):

    """A standard REST collection.

    This is a special type of resource in REST where a set of usually
    homogeneous, but at least related, resources are contained within a
    collection.  The collection is represented by the `url_path` (usually a
    plural noun) and each member of the collection is represented by a unique
    identifier under the collection in the URL path.  For example, a collection
    called "resources" might have individual members of the collection
    represented by "resources/1" and "resources/2".  In this case, "resources"
    would be the :attr:`url_path`, and "1" and "2" would be the values for
    :attr:`id`.

    An instance will represent either the collection or a member of the
    collection, depending on the `id` argument passed to the constructor.

    """

    id_type = str
    """The type of the :attr:`id` attribute.

    The :attr:`id_type` is `str` by default, since that is how it is
    represented in the resource URL, but it can be set to another type if the
    :attr:`id` attribute should be accepted and presented differently from its
    string representation.

    """

    def __init__(self, container, id=None):
        """Initialize an instance of this REST collection.

        `container` is interpreted the same as for `RestResource`.

        If `id` is None, the instance represents the collection rather than
        one of its members.

        """
        super().__init__(container)
        self._id = id = self.validate_id(id)
        if id is None:
            return
        self._url = urljoin(_with_trailing_slash(self._url), str(id))

    @classmethod
    def _from_url(cls, url, **kwargs):
        assert not kwargs, ("RestCollection._from_url should never receive "
                            "keyword arguments.")
        super_method = super()._from_url
        try:
            result = super_method(url)
        except ValueError:
            result = None
        url_split = _url_split(url)
        segments = url_split[2].split('/')
        try:
            id = cls.validate_id(segments.pop(-1))
        except ValueError:
            if result:
                return result
            raise
        url_split[2] = '/'.join(segments)
        collection_url = urlunsplit(url_split)
        member_result = tryf(super_method, collection_url, id=id)
        if result and member_result:
            raise ValueError(
                "The URL {!r} is ambiguous for {} as to whether "
                "it is for the collection or one of its members."
                .format(url, cls.__name__))
        return member_result or result
        # return cls(cls._get_container_from_url(collection_url), id=id)

    @classmethod
    def validate_id(cls, value):
        """Validate the given value as a valid identifier for this resource."""
        id = value
        if id is None:
            return id
        if not isinstance(value, cls.id_type):
            try:
                id = cls.id_type(id)
            except Exception as exc:
                raise ValueError(
                    "The id {!r} cannot be cast to {!r}.  {}"
                    .format(value, cls.id_type, str(exc)))
        if not str(id):
            raise ValueError(
                "The id {!r} has no string representation."
                .format(value))
        return id

    @property
    def id(self):
        """The identifier of the member within the REST collection.

        This is `None` if this instance represents the entire collection.

        """
        return self._id
