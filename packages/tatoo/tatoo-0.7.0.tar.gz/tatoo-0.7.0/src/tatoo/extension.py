# -*- coding: utf-8 -*-
"""
    tatoo.extension
    ~~~~~~~~~~~~~~~

    Tatoo extensions API.

"""

from __future__ import absolute_import, unicode_literals

from pkg_resources import WorkingSet

from zope.interface import implementer, implementer_only

from tatoo.utils import inherit_docs
from tatoo.utils.manager import Manager
from tatoo.interfaces import IExtension
from tatoo.signals import extension_load
from tatoo.utils.imports import qualname
from tatoo.interfaces import IExtensionManager
from tatoo.utils.lazy import LazyProxy, maybe_evaluate
from tatoo.utils.datastructures import AttributeDictMixin


def _lazy_task(extension, fun, kwargs):
    kwargs.setdefault('extension', extension)
    return extension.env.task(fun, **kwargs)


@inherit_docs
@implementer(IExtension)
class Extension(object):
    """This represents an extension."""

    env = None
    name = None
    enabled = True
    version = 'N/A'

    def __init__(self, name=None, enabled=None, version=None, env=None):
        self.env = env or self.env
        self.name = name or self.name or qualname(type(self))
        self.enabled = enabled if enabled is not None else self.enabled
        self.version = version or self.version

    def task(self, *args, **kwargs):
        """Decorator to create and bind tasks to the extension.

        Example::

            >>> from tatoo.extension import Extension
            >>> ext = Extension('myext')
            >>> @ext.task
            ... def add(x, y):
            ...     return x+y

        """
        def inner(ext, **opts):
            def wrapper(fun):
                # Since extensions don't know the exact environment
                # they will be bound to, instead of the task instance
                # we return LazyProxy instance here.
                # These proxies must be evaluated once the attr `env`
                # is set - so we connect to `extension_load` signal
                # and evaluate the proxy within.
                proxy = LazyProxy(_lazy_task, (ext, fun, opts))

                @extension_load.connect(weak=False)
                def evaluate_task(sender, **kwargs):
                    # pylint: disable=W0613,W0612
                    maybe_evaluate(proxy)

                return proxy
            return wrapper
        if len(args) == 1 and callable(args[0]):
            return inner(self, **kwargs)(args[0])
        return inner(self, **kwargs)

    def __repr__(self):
        return '<Extension: {0.alias}>'.format(self)

    def __str__(self):
        return self.name

    @property
    def alias(self):
        return self.name.rsplit('.', 1)[-1]

    def __reduce__(self):
        return (Extension, (self.name, self.enabled, self.version))


# pylint: disable=R0901
@inherit_docs
@implementer_only(IExtensionManager)
class ExtensionManager(Manager, AttributeDictMixin):
    """Extension manager."""
    interface = IExtension

    def __setitem__(self, name, extension):
        # Will raise AlreadyRegistered to prevent double registration
        super(ExtensionManager, self).__setitem__(name, extension)
        extension.env = self.env
        extension_load.send(sender=extension)

    def load_from_entry_points(self):  # pragma: no cover
        # Recreate WorkingSet on each call, so any installed module
        # in runtime will be properly picked.
        working_set = WorkingSet()
        for entrypoint in working_set.iter_entry_points('tatoo.extensions'):
            extension = entrypoint.load()
            self[extension.name] = extension
