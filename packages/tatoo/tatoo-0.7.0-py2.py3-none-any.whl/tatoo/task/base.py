# -*- coding: utf-8 -*-
"""

    tatoo.task.base
    ~~~~~~~~~~~~~~~

    This module contains base class for all tasks.

"""

from __future__ import absolute_import, unicode_literals

from six import reraise

from zope.interface import implementer
from zope.interface import implementer_only
from zope.interface.interfaces import ComponentLookupError

from tatoo.task.trace import Tracer  # pylint: disable=W0611
from tatoo.task.result import EagerResult  # pylint: disable=W0611

from tatoo.utils import uuid
from tatoo.utils import inherit_docs
from tatoo.utils import cached_property
from tatoo.utils.manager import Manager
from tatoo.utils.imports import instantiate
from tatoo.utils.datastructures import AttributeDict

from tatoo.signals import before_task_create

from tatoo.exceptions import ExceptionInfo
from tatoo.exceptions import TaskNotRegistered
from tatoo.exceptions import TaskAlreadyRegistered

from tatoo.interfaces import ITask
from tatoo.interfaces import ITracer
from tatoo.interfaces import ITaskManager

__all__ = ['Task']


UNNAMED_EXT = """\
Cannot automatically generate task name because extension is unnamed.
Either give a name for extension or explicitly specify task name.
"""


@inherit_docs  # pylint: disable=R0921
@implementer(ITask)
class Task(object):
    """Base class for all concrete tasks."""

    env = None
    name = None
    manager = None
    internal = False
    throws = ()
    parameters = ()
    validate_params = True

    EagerResult = EagerResult

    # Tracer function.
    __trace__ = None

    def __call__(*args, **kwargs):  # pylint: disable=E0211
        raise NotImplementedError  # pragma: no cover

    def apply(self, args=None, kwargs=None, **request):
        request['eager'] = True
        if 'request_id' not in request or request['request_id'] is None:
            request['request_id'] = uuid()
        request_id = request['request_id']
        request['args'] = args or ()
        request['kwargs'] = kwargs or {}
        request['name'] = self.name

        task = self.manager[self.name]
        tracer = self.manager.tracer

        ret = tracer.trace_task(task, request=request)

        retval = ret.retval
        traceback = None
        if isinstance(retval, ExceptionInfo):
            retval, traceback = retval.exception, retval.traceback

        return self.EagerResult(
            request_id, result=retval, state=ret.state, traceback=traceback,
            runtime=ret.runtime, env=self.env,
        )

    def request(self, **attrs):  # pylint: disable=R0201
        return AttributeDict(**attrs)
    r = request

    @property
    def __name__(self):
        return self.__class__.__name__


@implementer_only(ITaskManager)
class TaskManager(Manager):
    """The registry keeps track of tasks."""

    env = None
    interface = ITask

    Task = Task
    Tracer = Tracer

    def __getitem__(self, name):
        try:
            return super(TaskManager, self).__getitem__(name)
        except ComponentLookupError:
            reraise(TaskNotRegistered, TaskNotRegistered(name))

    def __iter__(self):
        for name in super(TaskManager, self).__iter__():
            if not self[name].internal:
                yield name

    @cached_property
    def tracer(self):
        try:
            return self.env.getUtility(ITracer)
        except ComponentLookupError:
            return instantiate(self.Tracer, env=self.env)

    def task_from_fun(self, fun, name=None, base=None, bind=False,
                      extension=None, **opts):
        env = self.env
        Task = base or self.Task  # pylint: disable=W0621
        if name and callable(name):
            name = name(self.env, fun)
        name = name or self.gen_task_name(fun, extension)

        if name in self:
            raise TaskAlreadyRegistered(
                'Task named {0} is already registered.'.format(name)
            )
        validate = opts.pop('validate_params',
                            env.settings['TATOO_VALIDATE_PARAMS'])
        before_task_create.send(sender=None, name=name, fun=fun, opts=opts)
        params = getattr(fun, '__tatoo_params__', [])
        run = fun if bind else staticmethod(fun)
        task = type(str(fun.__name__), (Task, ), dict(
            env=env,
            name=name,
            manager=self,
            parameters=params,
            validate_params=validate,
            __call__=run,
            __doc__=fun.__doc__,
            __module__=fun.__module__,
            __wrapped__=run,
            **opts
        ))()
        self[name] = task
        return task

    def gen_task_name(self, fun, extension=None):  # pylint: disable=R0201
        if extension is not None:
            if not extension.name:
                raise RuntimeError(UNNAMED_EXT)
            return '{0}.{1}'.format(extension.name, fun.__name__)
        return fun.__name__
