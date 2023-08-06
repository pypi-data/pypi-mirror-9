# -*- coding: utf-8 -*-
"""

    tatoo.utils.datastructures
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Collection of useful datastructures.

"""

from __future__ import absolute_import, unicode_literals

from itertools import chain
from collections import MutableMapping, Mapping

from six import iteritems, PY3

from tatoo.utils import isidentifier

__all__ = [
    'AttributeDictMixin', 'AttributeDict',
    'force_mapping', 'ConfigurationView'
]


class AttributeDictMixin(object):
    """Augment classes with a Mapping interface by adding attribute access.

    I.e. `d.key -> d[key]`.
    """

    # __setattr__ can cause infinite recursion when mixing e.g. MutableMapping
    # and setting attributes in its __init__.
    def __getattr__(self, key):
        """`d.key -> d[key]`"""
        try:
            return self[key]
        except KeyError:
            raise AttributeError(
                '{0!r} object has no attribute {1!r}'.format(
                    type(self).__name__, key
                )
            )


class AttributeDict(dict, AttributeDictMixin):
    """Dict subclass with attribute access."""

    def __setattr__(self, key, value):
        """`d[key] = value -> d.key = value`"""
        self[key] = value


class _DictAttribute(object):
    """Dict interface to attributes.

    `obj[k] -> obj.k`
    `obj[k] = val -> obj.k = val`
    """

    obj = None

    def __init__(self, obj):
        object.__setattr__(self, 'obj', obj)

    def __getattr__(self, key):
        return getattr(self.obj, key)

    def __setattr__(self, key, value):
        return setattr(self.obj, key, value)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key, default):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def __getitem__(self, key):
        try:
            return getattr(self.obj, key)
        except AttributeError:
            raise KeyError(key)

    def __setitem__(self, key, value):
        setattr(self.obj, key, value)

    def __contains__(self, key):
        return hasattr(self.obj, key)

    def _iterate_keys(self):
        return iter(dir(self.obj))
    iterkeys = _iterate_keys

    def __iter__(self):
        return self._iterate_keys()

    def _iterate_items(self):
        for key in self._iterate_keys():
            yield key, getattr(self.obj, key)
    iteritems = _iterate_items

    def _iterate_values(self):
        for key in self._iterate_keys():
            yield getattr(self.obj, key)
    itervalues = _iterate_values

    if PY3:
        items = _iterate_items
        keys = _iterate_keys
        values = _iterate_values
    else:  # pragma: no cover
        def keys(self):
            return list(self)

        def items(self):
            return list(self._iterate_items())

        def values(self):
            return list(self._iterate_values())


def force_mapping(obj):
    """Force `obj` to have mapping interface."""
    return _DictAttribute(obj) if not isinstance(obj, Mapping) else obj


class ConfigurationView(AttributeDictMixin):
    """A view over an applications configuration dicts.

    If the key does not exist in ``chages``, the ``defaults`` dict
    are consulted.
    """

    changes = None
    defaults = None

    def __init__(self, changes, defaults):
        self.__dict__.update(changes=changes or {},
                             defaults=defaults or {})

    def add_defaults(self, defaults):
        """Add new default values."""
        self.defaults.update(defaults)

    def __getitem__(self, key):
        try:
            return self.changes[key]
        except KeyError:
            return self.defaults[key]

    def __setitem__(self, key, value):
        if not isidentifier(key):
            raise TypeError('{0} is not a valid identifier'.format(key))
        self.changes[key] = value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def clear(self):
        """Remove all changes, but keep defaults."""
        self.changes.clear()

    def setdefault(self, key, default):
        try:
            return self[key]
        except KeyError:
            self.defaults[key] = default
            return default

    def update(self, *args, **kwargs):
        return self.changes.update(*args, **kwargs)

    def __contains__(self, key):
        return any(key in m for m in (self.changes, self.defaults))

    def __bool__(self):
        return any((self.changes, self.defaults))
    __nonzero__ = __bool__

    def __repr__(self):
        return repr(dict(iteritems(self)))

    def __iter__(self):
        return self._iterate_keys()

    def __len__(self):
        return len(self.changes) + len(self.defaults)

    def _iter(self):
        return chain(self.changes, self.defaults)

    def _iterate_keys(self):
        return self._iter()
    iterkeys = _iterate_keys

    def _iterate_items(self):
        return ((key, self[key]) for key in self)
    iteritems = _iterate_items

    def _iterate_values(self):
        return (self[key] for key in self)
    itervalues = _iterate_values

    if PY3:
        keys = _iterate_keys
        items = _iterate_items
        values = _iterate_values
    else:
        def keys(self):
            return list(self._iterate_keys())

        def items(self):
            return list(self._iterate_items())

        def values(self):
            return list(self._iterate_values())

MutableMapping.register(ConfigurationView)
