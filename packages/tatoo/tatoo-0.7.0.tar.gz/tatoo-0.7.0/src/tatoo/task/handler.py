# -*- coding: utf-8 -*-
"""

    tatoo.task.handler
    ~~~~~~~~~~~~~~~~~~

    Task execution handlers.

"""

from __future__ import absolute_import, unicode_literals

import sys
import logging

from zope.interface import implementer

from tatoo import signals
from tatoo.utils import inherit_docs
from tatoo.utils.text import truncate
from tatoo.utils import cached_property
from tatoo.exceptions import ExceptionInfo
from tatoo.utils.encoding import safe_repr
from tatoo.interfaces import IResultHandler
from tatoo.utils.serialization import get_pickleable_etype
from tatoo.utils.serialization import get_pickled_exception
from tatoo.utils.serialization import get_pickleable_exception

LOG_FORMAT = 'Task %(name)s [%(id)s] %(description)s'


@implementer(IResultHandler)
class BaseHandler(object):

    env = None
    log_format = LOG_FORMAT + ' in %(runtime)0.6fs: %(retval)s'
    severity = logging.INFO
    exc_info = False

    def __init__(self, env=None):
        self.env = env or self.env

    def _log_message(self, task, request, retval, einfo=None, extra=None):
        exc_info = exc = eobj = None
        if einfo is not None:
            eobj = einfo.exception = get_pickled_exception(einfo.exception)
            exc = safe_repr(eobj)
            exc_info = einfo.exc_info
        args = safe_repr(request['args'])
        kwargs = safe_repr(request['kwargs'])

        context = {
            'id': request['request_id'],
            'name': task.name,
            'retval': exc if einfo is not None else retval,
            'args': args,
            'kwargs': kwargs,
        }
        context.update(extra or {})
        self.logger.log(
            self.severity, self.log_format.strip(), context,
            exc_info=exc_info if self.exc_info else None,
            extra={'data': context},
        )

    @cached_property
    def logger(self):
        return self.env.logger.get_logger(__name__)


@inherit_docs
class SuccessHandler(BaseHandler):
    """Success handler."""

    def __call__(self, task, request, retval, runtime,
                 INFO=logging.INFO):
        Rstr = truncate(safe_repr(retval), 256)
        if self.logger.isEnabledFor(INFO):
            extra = {'description': 'succeeded',
                     'runtime': runtime}
            self._log_message(task, request, Rstr, extra=extra)
        return Rstr


@inherit_docs
class IgnoreHandler(BaseHandler):
    """Ignore handler."""

    log_format = LOG_FORMAT

    def __call__(self, task, request, retval, runtime):
        einfo = ExceptionInfo(internal=True)
        extra = {'description': 'ignored'}
        self._log_message(task, request, einfo, extra=extra)
        return einfo


@inherit_docs
class FailureHandler(BaseHandler):
    """Failure handler."""

    severity = logging.CRITICAL
    exc_info = True
    description = 'INTERNAL ERROR'

    def __call__(self, task, request, retval, runtime,
                 INFO=logging.INFO):
        _, _, traceback = sys.exc_info()
        try:
            exc = retval
            einfo = ExceptionInfo()
            einfo.exception = get_pickleable_exception(einfo.exception)
            einfo.type = get_pickleable_etype(einfo.type)
            signals.task_failure.send(
                sender=task, request=request, exception=exc,
                traceback=traceback, einfo=einfo,
            )
            if not einfo.internal:
                if task.throws and any(isinstance(exc, t)
                                       for t in task.throws):
                    self.severity = INFO
                    self.exc_info = False
                    self.description = 'raised expected'
                else:
                    self.description = 'raised unexpected'
            extra = {'description': self.description,
                     'runtime': runtime}
            self._log_message(task, request, retval,
                              einfo=einfo, extra=extra)
            return einfo
        finally:
            del traceback
