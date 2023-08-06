# -*- coding: utf-8 -*-
"""

    tatoo.task.result
    ~~~~~~~~~~~~~~~~~

    Defines :class:`BaseResult` abstract class, instances of subclasses of
    :class:`BaseResult` are used to represent a task execution results.

"""

# pylint: disable=R0922
from __future__ import absolute_import, unicode_literals

from abc import ABCMeta, abstractmethod

from six import string_types, add_metaclass

from zope.interface import implementer

from tatoo.utils import inherit_docs
from tatoo.interfaces import ITaskResult

_NOTREADY = object()


@inherit_docs
@add_metaclass(ABCMeta)
@implementer(ITaskResult)
class BaseResult(object):
    """Base class for all result implementations."""

    env = None

    def __init__(self, request_id, env=None):
        self.request_id = request_id
        self.env = env or self.env

    def get(self, propagate=True):
        result = self.get_execution_meta()['result']
        if propagate:
            self.maybe_reraise(result)
        return result

    def ready(self):
        return self.result is not _NOTREADY

    def successful(self):
        return self.state == 'SUCCESS'

    def failed(self):
        return self.state == 'FAILURE'

    def maybe_reraise(self, result):
        """If the state is in propagate states (e.g. the result is
        an instance of :class:`Exception`), raise the result.
        """
        if self.state == 'FAILURE':
            raise result

    def __str__(self):
        return str(self.request_id)

    def __hash__(self):
        return hash(self.request_id)

    def __repr__(self):
        return '<{0}: {1}>'.format(type(self).__name__, self.request_id)

    def __eq__(self, other):
        if isinstance(other, BaseResult):
            return other.request_id == self.request_id
        elif isinstance(other, string_types):
            return other == self.request_id
        return NotImplemented

    @property
    def result(self):
        return self.get(propagate=True)

    @property
    def traceback(self):
        return self.get_execution_meta()['traceback']

    @property
    def state(self):
        return self.get_execution_meta()['state']

    @property
    def runtime(self):
        return self.get_execution_meta()['runtime']

    @abstractmethod
    def get_execution_meta(self):
        """Used to get the execution meta information, like
        result, state, traceback and runtime.
        """


class EagerResult(BaseResult):
    """Result of locally tracered task execution."""

    def __init__(self, request_id, result=_NOTREADY, state=None, runtime=None,
                 traceback=None, env=None):
        super(EagerResult, self).__init__(request_id, env=env)
        self._result = result
        self._state = state
        self._runtime = runtime
        self._traceback = traceback

    def get_execution_meta(self):
        return {
            'result': self._result,
            'state': self._state,
            'traceback': self._traceback,
            'runtime': self._runtime,
        }
