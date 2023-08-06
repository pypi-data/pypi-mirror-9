# -*- coding: utf-8 -*-
"""

    tatoo.task.trace
    ~~~~~~~~~~~~~~~~

    Routines to trace task execution, log execution results, failures,
    to do pre-execution and post-execution actions and so on.

"""

# pylint: disable=W0703
from __future__ import absolute_import, unicode_literals

import sys
from collections import namedtuple

from zope.interface import implementer

from tatoo.interfaces import ITracer

from tatoo import signals
from tatoo.utils import inherit_docs
from tatoo.utils import cached_property
from tatoo.utils.times import monotonic

from tatoo.exceptions import ExceptionInfo
from tatoo.exceptions import TaskSpecificException

from tatoo.interfaces import IResultHandler
from tatoo.utils.serialization import get_pickleable_exception

from tatoo.task.handler import IgnoreHandler
from tatoo.task.handler import SuccessHandler
from tatoo.task.handler import FailureHandler


def report_internal_error(logger, exc, Info=ExceptionInfo):
    """Warns when an internal error is encountered."""
    _type, _, _tb = sys.exc_info()
    try:
        _value = get_pickleable_exception(exc)
        exc_info = Info((_type, _value, _tb), internal=True)
        logger.warning(
            'Exception raised outside body: {0!r}:\n{1}'.format(
                exc, exc_info.traceback
            )
        )
        return exc_info
    finally:
        del _tb


@inherit_docs
@implementer(ITracer)
class Tracer(object):
    """Task execution tracer."""
    env = None

    trace_ok_t = namedtuple(
        'trace_ok_t', ('retval', 'state', 'runtime', 'retstr')
    )

    def __init__(self, env=None):
        env = self.env = env or self.env
        env.registerUtility(SuccessHandler(env), name='SUCCESS')
        env.registerUtility(IgnoreHandler(env), name='IGNORED')
        env.registerUtility(FailureHandler(env), name='FAILURE')

    def build_tracer(self, task, monotonic=monotonic):
        # pylint: disable=W0621,R0914

        trace_ok_t = self.trace_ok_t
        _report_internal_error = report_internal_error

        # Cache signal methods
        send_prerun = signals.task_prerun.send
        send_postrun = signals.task_postrun.send
        send_success = signals.task_success.send
        send_cleanup = signals.task_cleanup.send

        def on_return(request, retval, runtime, state='FAILURE'):
            if isinstance(retval, TaskSpecificException):
                state = retval.state

            handler = self.env.getUtility(IResultHandler, name=state)
            R = handler(task, request, retval, runtime)
            return R, state, retval

        def trace_task(request):
            """Function used to actually trace task execution."""
            # pylint: disable=R0912
            # R - is the possibly prepared return value
            # T - time of run
            # Rstr - textual representation of return value
            # retval - is unmodified return value
            # state - is the resulting task state
            R = T = Rstr = retval = state = None
            time_start = monotonic()
            try:
                # push_request(request)
                try:
                    # PRE
                    send_prerun(sender=task, request=request)
                    # TRACE
                    try:
                        R = retval = task(*request['args'],
                                          **request['kwargs'])
                        T = monotonic() - time_start
                        state = 'SUCCESS'
                    except Exception as exc:
                        T = monotonic() - time_start
                        R, state, retval = on_return(
                            request, exc, runtime=T
                        )
                    except BaseException:
                        raise
                    else:
                        Rstr, state, R = on_return(
                            request, retval, runtime=T, state=state,
                        )
                        send_success(
                            sender=task, result=retval, request=request
                        )
                finally:
                    try:
                        send_postrun(
                            sender=task, retval=retval, state=state,
                            request=request
                        )
                    finally:
                        # pop_request()
                        try:
                            send_cleanup(sender=task)
                        except (KeyboardInterrupt, SystemExit, MemoryError):
                            raise
                        except Exception as exc:
                            self.logger.error(
                                'Process cleanup failed: %r',
                                exc, exc_info=True
                            )
            except MemoryError:
                raise
            except Exception as exc:
                R = _report_internal_error(self.logger, exc)
                T = monotonic() - time_start
                if request is not None:
                    _, state, _ = on_return(request, exc, runtime=T)
            return trace_ok_t(R, state, T, Rstr)

        return trace_task

    def trace_task(self, task, request, tracer=None):
        """Trace task execution.

        :param task: The task instance found in `env.tasks` registry.
        :param request: Execution request.
        """
        try:
            if tracer is not None:
                return tracer(request)
            if task.__trace__ is None:
                task.__trace__ = self.build_tracer(task)
            return task.__trace__(request)
        except Exception as exc:
            if request['eager']:
                raise
            return self.trace_ok_t(report_internal_error(self.logger, exc),
                                   'FAILURE', 0.0, None)

    @cached_property
    def logger(self):
        return self.env.logger.get_logger(__name__)
