# -*- coding: utf-8 -*-
"""

    tatoo.utils.imports
    ~~~~~~~~~~~~~~~~~~~

    Utilities to deal with dynamic imports.

"""

from __future__ import absolute_import, unicode_literals

import os
import sys
from importlib import import_module
from contextlib import contextmanager

from six import reraise, string_types

__all__ = [
    'symbol_by_name', 'instantiate', 'import_from_cwd',
]


def symbol_by_name(name, aliases=None, imp=import_module, package=None,
                   sep='.', default=None, **kwargs):
    """Get symbol by qualified name.

    The name should be the full dot-separated path to the class::

        modulename.ClassName

    Example::

        a.b.c.Class
             ^- class name

    or using ':' to separate module and symbol::

        a.b.c:Class

    If `aliases` is provided, a dict containing short name/long name
    mappings, the name is looked up in the aliases first.

    Examples:

        >>> symbol_by_name('a.b.c.Class')
        <class 'a.b.c.Class'>

        >>> symbol_by_name('default', {
        ...     'default': 'a.b.c.Class'})
        <class 'a.b.c.Class'>

        # Does not try to look up non-string names.
        >>> from a.b.c import Class
        >>> symbol_by_name(Class) is Class
        True

    """
    if not isinstance(name, string_types):
        return name  # already a class

    name = (aliases or {}).get(name) or name
    sep = ':' if ':' in name else sep
    module_name, _, cls_name = name.rpartition(sep)
    if not module_name:
        cls_name, module_name = None, package if package else cls_name
    try:
        try:
            module = imp(module_name, package=package, **kwargs)
        except ImportError as exc:
            reraise(ImportError,
                    ImportError("Couldn't import {0!r}: {1}".format(
                        name, exc
                    )),
                    sys.exc_info()[2])
        return getattr(module, cls_name) if cls_name else module
    except (ImportError, AttributeError):
        if default is None:
            raise
    return default


def instantiate(name, *args, **kwargs):
    """Instantiate class by name."""
    return symbol_by_name(name)(*args, **kwargs)


@contextmanager
def cwd_in_path():
    cwd = os.getcwd()
    sys.path.insert(0, cwd)
    try:
        yield cwd
    finally:
        try:
            sys.path.remove(cwd)
        except ValueError:  # pragma: no cover
            pass


def import_from_cwd(module, imp=import_module, package=None):
    """Import module, but make sure it finds modules
    located in the current directory.

    Modules located in the current directory has
    precedence over modules located in `sys.path`.
    """
    with cwd_in_path():
        return imp(module, package=package)


if sys.version_info >= (3, 4):
    def qualname(obj):
        if not hasattr(obj, '__name__') and hasattr(obj, '__class__'):
            obj = obj.__class__
        _qualname = getattr(obj, '__qualname__', None)
        if '.' not in _qualname:
            _qualname = '.'.join((obj.__module__, _qualname))
        return _qualname
else:  # pragma: no cover
    def qualname(obj):
        if not hasattr(obj, '__name__') and hasattr(obj, '__class__'):
            obj = obj.__class__
        return '.'.join((obj.__module__, obj.__name__))
