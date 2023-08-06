# -*- coding: utf-8 -*-
"""

    tatoo.utils
    ~~~~~~~~~~~~

    Helper functions and classes.

"""

from __future__ import absolute_import, unicode_literals, print_function

from uuid import uuid4

from six import PY2

from zope.interface import implementedBy
try:
    from inspect import signature
except ImportError:  # pragma: no cover
    from funcsigs import signature

__all__ = ['cached_property', 'uuid', 'signature']

if PY2:  # pragma: no cover
    import re
    import tokenize
    from keyword import iskeyword

    def isidentifier(string, pattern=tokenize.Name + '$'):
        return re.match(pattern, string) and not iskeyword(string)
else:
    def isidentifier(string):
        return string.isidentifier()


class cached_property(object):
    """Property descriptor that caches the return value
    of the get function.

    *Examples*

    .. code-block:: python

        @cached_property
        def connection(self):
            return Connection()

        @connection.setter  # Prepares stored value
        def connection(self, value):
            if value is None:
                raise TypeError('Connection must be a connection')
            return value

        @connection.deleter
        def connection(self, value):
            # Additional action to do at del(self.attr)
            if value is not None:
                print('Connection {0!r} deleted'.format(value)

    """

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.__get = fget
        self.__set = fset
        self.__del = fdel
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__

    def __get__(self, obj, type_=None):
        if obj is None:
            return self
        try:
            return obj.__dict__[self.__name__]
        except KeyError:
            value = obj.__dict__[self.__name__] = self.__get(obj)
            return value

    def __set__(self, obj, value):
        if obj is None:
            return self
        if self.__set is not None:
            value = self.__set(obj, value)
        obj.__dict__[self.__name__] = value

    def __delete__(self, obj):
        if obj is None:
            return self
        try:
            value = obj.__dict__.pop(self.__name__)
        except KeyError:
            pass
        else:
            if self.__del is not None:
                self.__del(obj, value)

    def setter(self, fset):
        return self.__class__(self.__get, fset, self.__del)

    def deleter(self, fdel):
        return self.__class__(self.__get, self.__set, fdel)


def _iro(*bases):
    """Slightly modified
    http://code.activestate.com/recipes/577748-calculate-the-mro-of-a-class/
    to handle zope interfaces.

    Calculate the Method Resolution Order of bases using the C3 algorithm.

    Suppose you intended creating a class K with the given base classes. This
    function returns the MRO which K would have, *excluding* K itself (since
    it doesn't yet exist), as if you had actually created the class.

    Another way of looking at this, if you pass a single class K, this will
    return the linearization of K (the MRO of K, *including* itself).
    """
    seqs = [list(C.__iro__) for C in bases] + [list(bases)]
    res = []
    while True:
        non_empty = list(filter(None, seqs))  # pylint: disable=W0141
        if not non_empty:
            # Nothing left to process, we're done.
            return tuple(res)
        for seq in non_empty:  # Find merge candidates among seq heads.
            candidate = seq[0]
            not_head = [s for s in non_empty if candidate in s[1:]]
            if not_head:
                # Reject the candidate.
                candidate = None
            else:
                break
        if not candidate:
            raise TypeError("inconsistent hierarchy, no C3 MRO is possible")
        res.append(candidate)
        for seq in non_empty:
            # Remove candidate.
            if seq[0] == candidate:
                del seq[0]


def inherit_docs(cls):
    """Class decorator allows to inherit docstrings from implemented
    interfaces. Not that it must be applied last, e.g.::

        @inherit_docs
        @implementer(IOne, ITwo)
        class Three(object):
            pass

    """
    iro = _iro(*implementedBy(cls))
    for name, method in vars(cls).items():
        if callable(method) and not method.__doc__:
            for interface in iro:
                imethod = interface.get(name)
                if imethod and imethod.__doc__:
                    method.__doc__ = imethod.__doc__
                    break
    return cls


def uuid(implementation=uuid4):
    """Generate a unique id, having - hopefully - a very small chance
    of collision.

    For now this is provided by :func:`uuid.uuid4`.
    """
    return str(implementation())
