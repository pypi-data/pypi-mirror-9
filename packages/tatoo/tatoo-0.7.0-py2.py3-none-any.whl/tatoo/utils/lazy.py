# -*- coding: utf-8 -*-
"""

    tatoo.utils.lazy
    ~~~~~~~~~~~~~~~~~

    Contains classes and methods related to deferred access
    and/or evaluation.

"""

# pylint: disable=W0212,E0602,W0142
from __future__ import absolute_import, unicode_literals

from six import text_type, PY3

__all__ = ['Proxy', 'LazyProxy', 'maybe_evaluate']

__module__ = __name__  # used by Proxy class body


# Code stolen from celery & werkzeug.local

def _default_cls_attr(name, type_, cls_value):
    # Proxy uses properties to forward the standard
    # class attributes __module__, __name__ and __doc__
    # to object, but these needs to be a string when
    # accessed from the Proxy class directly.

    def __new__(cls, getter):
        instance = type_.__new__(cls, cls_value)
        instance.__getter = getter
        return instance

    def __get__(self, obj, cls=None):  # pylint: disable=W0613
        return self.__getter(obj) if obj is not None else self

    return type(str(name), (type_,), {
        '__new__': __new__, '__get__': __get__,
    })


class Proxy(object):
    """Proxy to another object."""
    __slots__ = ('__proxied', '__args', '__kwargs')

    def __init__(self, proxied, args=None, kwargs=None):
        object.__setattr__(self, '_Proxy__proxied', proxied)
        object.__setattr__(self, '_Proxy__args', args or ())
        object.__setattr__(self, '_Proxy__kwargs', kwargs or {})

    @_default_cls_attr('name', str, __name__)
    def __name__(self):
        return self._get_current_object().__name__

    @_default_cls_attr('module', str, __module__)
    def __module__(self):
        return self._get_current_object().__module__

    @_default_cls_attr('doc', str, __doc__)
    def __doc__(self):
        return self._get_current_object().__doc__

    def _get_class(self):
        return self._get_current_object().__class__

    @property
    def __class__(self):
        return self._get_class()

    def _get_current_object(self):
        """Return the current object. This is useful if you want the real
        object behind the proxy at a time for performance reasons or because
        you want to pass the object into a different context.
        """
        obj = proxied = self.__proxied
        if callable(proxied):
            obj = proxied(*self.__args, **self.__kwargs)
        return obj

    @property
    def __dict__(self):
        try:
            return self._get_current_object().__dict__
        except RuntimeError:  # pragma: no cover
            raise AttributeError('__dict__')

    def __repr__(self):
        try:
            obj = self._get_current_object()
        except RuntimeError:  # pragma: no cover
            return '<{0} unbound>'.format(self.__class__.__name__)
        return repr(obj)

    def __bool__(self):
        try:
            return bool(self._get_current_object())
        except RuntimeError:  # pragma: no cover
            return False
    __nonzero__ = __bool__  # Py2

    def __unicode__(self):
        try:
            return text_type(self._get_current_object())
        except RuntimeError:
            return repr(self)

    def __dir__(self):
        try:
            return dir(self._get_current_object())
        except RuntimeError:  # pragma: no cover
            return []

    def __getattr__(self, name):
        if name == '__members__':
            return dir(self._get_current_object())
        return getattr(self._get_current_object(), name)

    def __setitem__(self, key, value):
        self._get_current_object()[key] = value

    def __delitem__(self, key):
        del self._get_current_object()[key]

    def __setslice__(self, i, j, seq):
        self._get_current_object()[i:j] = seq

    def __delslice__(self, i, j):
        del self._get_current_object()[i:j]

    __setattr__ = lambda x, n, v: setattr(x._get_current_object(), n, v)
    __delattr__ = lambda x, n: delattr(x._get_current_object(), n)
    __str__ = lambda x: str(x._get_current_object())
    __lt__ = lambda x, o: x._get_current_object() < o
    __le__ = lambda x, o: x._get_current_object() <= o
    __eq__ = lambda x, o: x._get_current_object() == o
    __ne__ = lambda x, o: x._get_current_object() != o
    __gt__ = lambda x, o: x._get_current_object() > o
    __ge__ = lambda x, o: x._get_current_object() >= o
    __hash__ = lambda x: hash(x._get_current_object())
    __call__ = lambda x, *a, **kw: x._get_current_object()(*a, **kw)
    __len__ = lambda x: len(x._get_current_object())
    __getitem__ = lambda x, i: x._get_current_object()[i]
    __iter__ = lambda x: iter(x._get_current_object())
    __contains__ = lambda x, i: i in x._get_current_object()
    __getslice__ = lambda x, i, j: x._get_current_object()[i:j]
    __add__ = lambda x, o: x._get_current_object() + o
    __sub__ = lambda x, o: x._get_current_object() - o
    __mul__ = lambda x, o: x._get_current_object() * o
    __floordiv__ = lambda x, o: x._get_current_object() // o
    __mod__ = lambda x, o: x._get_current_object() % o
    __divmod__ = lambda x, o: x._get_current_object().__divmod__(o)
    __pow__ = lambda x, o: x._get_current_object() ** o
    __lshift__ = lambda x, o: x._get_current_object() << o
    __rshift__ = lambda x, o: x._get_current_object() >> o
    __and__ = lambda x, o: x._get_current_object() & o
    __xor__ = lambda x, o: x._get_current_object() ^ o
    __or__ = lambda x, o: x._get_current_object() | o
    __div__ = lambda x, o: x._get_current_object().__div__(o)
    __truediv__ = lambda x, o: x._get_current_object().__truediv__(o)
    __neg__ = lambda x: -(x._get_current_object())
    __pos__ = lambda x: +(x._get_current_object())
    __abs__ = lambda x: abs(x._get_current_object())
    __invert__ = lambda x: ~(x._get_current_object())
    __complex__ = lambda x: complex(x._get_current_object())
    __int__ = lambda x: int(x._get_current_object())
    __float__ = lambda x: float(x._get_current_object())
    __oct__ = lambda x: oct(x._get_current_object())
    __hex__ = lambda x: hex(x._get_current_object())
    __index__ = lambda x: x._get_current_object().__index__()
    __coerce__ = lambda x, o: x._get_current_object().__coerce__(o)
    __enter__ = lambda x: x._get_current_object().__enter__()
    __exit__ = lambda x, *a, **kw: x._get_current_object().__exit__(*a, **kw)
    __reduce__ = lambda x: x._get_current_object().__reduce__()

    if not PY3:  # pragma: no cover
        __cmp__ = lambda x, o: cmp(x._get_current_object(), o)  # noqa
        __long__ = lambda x: long(x._get_current_object())      # noqa


class LazyProxy(Proxy):
    """Proxy to an object that has not yet been evaluated.

    :class:`Proxy` will evaluate the object each time,
    while :class:`LazyProxy` will only evaluate it once.
    """

    __slots__ = ('__pending__', '__evaluated')

    def _get_current_object(self):
        try:
            return object.__getattribute__(self, '_LazyProxy__evaluated')
        except AttributeError:
            return self.__evaluate__()

    def __then__(self, fun, *args, **kwargs):
        if self.__evaluated__():
            return fun(self._get_current_object(), *args, **kwargs)
        try:
            pending = object.__getattribute__(self, '__pending__')
        except AttributeError:
            pending = None
        if pending is None:
            from collections import deque
            pending = deque()
            object.__setattr__(self, '__pending__', pending)
        pending.append((fun, args, kwargs))

    def __evaluated__(self):
        try:
            object.__getattribute__(self, '_LazyProxy__evaluated')
        except AttributeError:
            return False
        return True

    def __maybe_evaluate__(self):
        return self._get_current_object()

    def __evaluate__(self,
                     _clean=('_Proxy__proxied',
                             '_Proxy__args',
                             '_Proxy__kwargs')):
        # Let it fail
        obj = super(LazyProxy, self)._get_current_object()
        object.__setattr__(self, '_LazyProxy__evaluated', obj)
        for attr in _clean:
            try:
                object.__delattr__(self, attr)
            except AttributeError:  # pragma: no cover
                pass

        # Call all functions registered themselves
        # using `__then__` method on the object evaluation.
        try:
            pending = object.__getattribute__(self, '__pending__')
        except AttributeError:
            pass
        else:
            try:
                while pending:
                    fun, args, kwargs = pending.popleft()
                    fun(obj, *args, **kwargs)
            finally:
                try:
                    object.__delattr__(self, '__pending__')
                except AttributeError:  # pragma: no cover
                    pass
        return obj


def maybe_evaluate(obj):
    """Try to evaluate and return the passed object."""
    try:
        return obj.__maybe_evaluate__()
    except AttributeError:
        return obj
