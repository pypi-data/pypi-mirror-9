# -*- coding: utf-8 -*-
"""

    tatoo.environment
    ~~~~~~~~~~~~~~~~~

    Runtime environment.

"""
from __future__ import absolute_import, unicode_literals

from zope.interface import implementer
from zope.interface.registry import Components
from zope.interface.interfaces import ComponentLookupError

from tatoo.log import Logger  # pylint: disable=W0611
from tatoo.utils import inherit_docs
from tatoo.settings import Settings  # pylint: disable=W0611
from tatoo.task.base import TaskManager  # pylint: disable=W0611
from tatoo.utils import cached_property
from tatoo.utils.bugreport import bugreport
from tatoo.extension import ExtensionManager  # pylint: disable=W0611
from tatoo.utils.imports import symbol_by_name, instantiate

from tatoo.interfaces import ILogger
from tatoo.interfaces import ISettings
from tatoo.interfaces import IEnvironment
from tatoo.interfaces import ITaskManager
from tatoo.interfaces import IExtensionManager

__all__ = ['Environment']


@inherit_docs
@implementer(IEnvironment)
class Environment(Components):
    """Tatoo environment."""

    #: Environment name.
    name = None

    Logger = Logger
    Settings = Settings
    TaskManager = TaskManager
    ExtensionManager = ExtensionManager

    def __init__(self, name=None, settings=None):
        self.name = name or self.name
        super(Environment, self).__init__(self.name)
        if settings is not None:
            try:
                implemented = ISettings.providedBy(settings)
                if implemented:
                    self.settings.changes = settings.changes
                    self.settings.defaults = settings.defaults
            except TypeError:
                implemented = False
            if not implemented:
                self.settings.update(settings)

    def task(self, *args, **kwargs):
        """Decorator to create and bind tasks to the env.

        Example::

            >>> from tatoo import Environment
            >>> env = Environment()
            >>> @env.task
            ... def add(x, y):
            ...     return x+y

        """
        def inner(env, **opts):
            def wrapper(fun):
                return env.tasks.task_from_fun(fun, **opts)
            return wrapper
        if len(args) == 1 and callable(args[0]):
            return inner(self, **kwargs)(args[0])
        return inner(self, **kwargs)

    def bugreport(self):
        return bugreport(self)

    def subclass_with_self(self, cls, name=None, attr='env',
                           reverse_name=None,
                           **kwargs):
        cls = symbol_by_name(cls)
        reverse_name = reverse_name or cls.__name__

        attrs = dict({attr: self}, __module__=cls.__module__,
                     __doc__=cls.__doc__, **kwargs)
        return type(str(name or cls.__name__), (cls,), attrs)

    @cached_property
    def tasks(self):
        try:
            return self.getUtility(ITaskManager)
        except ComponentLookupError:
            tasks = instantiate(self.TaskManager, env=self)
            self.registerUtility(tasks)
            return tasks

    @cached_property
    def settings(self):
        try:
            return self.getUtility(ISettings)
        except ComponentLookupError:
            settings = instantiate(self.Settings)
            self.registerUtility(settings)
            return settings

    @cached_property
    def logger(self):
        try:
            return self.getUtility(ILogger)
        except ComponentLookupError:
            logger = instantiate(self.Logger, env=self)
            self.registerUtility(logger)
            return logger

    @cached_property
    def extensions(self):
        try:
            return self.getUtility(IExtensionManager)
        except ComponentLookupError:
            extensions = instantiate(self.ExtensionManager, env=self)
            self.registerUtility(extensions)
            return extensions

    def __repr__(self):
        return '<Environment {0!r}: {1}>'.format(self.name, id(self))

    def __reduce__(self):
        return (Environment, (self.name, self.settings))
