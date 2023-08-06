# -*- coding: utf-8 -*-
"""
    tatoo.exceptions
    ~~~~~~~~~~~~~~~~

    All exceptions are defined here.

"""
from __future__ import absolute_import, unicode_literals

from .einfo import ExceptionInfo

__all__ = [
    'ExceptionInfo', 'TaskSpecificException', 'Ignore',
    'InvalidTaskError', 'TaskAlreadyRegistered', 'TaskNotRegistered',
]


class TaskSpecificException(Exception):
    """Task-specific exceptions must subclass this type to be properly
    cached and handled as specific cases, not general errors.

    Example of task-specific exception is :exc:`Ignore`.
    """


class Ignore(TaskSpecificException):
    """A task can raise this to ignore doing state updates."""
    state = 'IGNORED'


class InvalidTaskError(Exception):
    """The task has invalid data or is not properly constructed."""


class TaskAlreadyRegistered(RuntimeError):
    """Raised when trying to register a task with already registered
    name.
    """


class TaskNotRegistered(KeyError):
    """Raised when accessing a not registered task."""
