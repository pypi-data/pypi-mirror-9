# -*- coding: utf-8 -*-
"""

    tatoo.utils.manager
    ~~~~~~~~~~~~~~~~~~~~

    Contains general class to create managers.

"""

from __future__ import absolute_import, unicode_literals

from six import reraise

from collections import MutableMapping

from zope.interface import implementer
from zope.interface.interfaces import ComponentLookupError

from tatoo.interfaces import IManager


@implementer(IManager)
class Manager(MutableMapping):
    """The manager keeps track of objects."""

    env = None
    interface = None
    strict = True

    AlreadyRegistered = RuntimeError
    NotRegistered = KeyError

    def __init__(self, env=None, strict=None, *args, **kwargs):
        super(Manager, self).__init__(*args, **kwargs)
        self.env = env or self.env
        self.strict = strict if strict is not None else self.strict

    def __getitem__(self, name):
        try:
            return self.env.getUtility(self.interface, name)
        except ComponentLookupError:
            reraise(self.NotRegistered, self.NotRegistered(name))

    def __setitem__(self, name, extension):
        if self.strict and name in self:
            raise self.AlreadyRegistered(name)
        self.env.registerUtility(extension, name=name)

    def __delitem__(self, name):
        try:
            self.env.unregisterUtility(self.interface, name)
        except ComponentLookupError:
            reraise(self.NotRegistered, self.NotRegistered(name))

    def __iter__(self):
        objs = self.env.getAllUtilitiesRegisteredFor(self.interface)
        return iter(obj.name for obj in objs)

    def __len__(self):
        return len(self.env.getAllUtilitiesRegisteredFor(self.interface))
