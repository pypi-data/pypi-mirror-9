# -*- coding: utf-8 -*-
"""

    tatoo.task.parameter
    ~~~~~~~~~~~~~~~~~~~~

    Helper decorator to declare task parameters.

"""

from __future__ import absolute_import, unicode_literals

import inspect
from copy import deepcopy
from functools import partial

from tatoo.utils import signature
from tatoo.interfaces import ITask
from tatoo.signals import task_prerun
from tatoo.utils.lazy import LazyProxy
from tatoo.task.types import _convert_type

__all__ = ['parameter']


def make_default_short_help(help, max_length=45):
    words = help.split()
    total_length = 0
    result = []
    done = False

    for word in words:
        if word[-1:] == '.':
            done = True
        new_length = result and 1 + len(word) or len(word)
        if total_length + new_length > max_length:
            result.append('...')
            done = True
        else:
            if result:
                result.append(' ')
            result.append(word)
        if done:
            break
        total_length += new_length

    return ''.join(result)


class Parameter(object):
    """This represents a parameter which can be either an argument or
    an option.

    :param dest: The name of the argument that should be passed to the
        command's callback.

    :param options: If the parameter should act like an option, this
        should be a list of options.

    :keyword type: The type that should be used. Either a :class:`Parameter`
        instance or a python type. The latter is converted into the former
        automatically if supported.

    :keyword required: Controls if this parameter is optional or not.
    :keyword default: The default value if omitted.
    :keyword help: The help string.
    :keword short_help: Optional short version of the help string.

    :keyword metavar: Controls how the value should be represented
        in the help page.

    :keyword envvar: A string or list of strings that are environment
        variables that should be checked.
    """

    def __init__(self, dest, options=None, type=None, required=None,
                 nargs=1, default=None, help=None, short_help=None,
                 metavar=None, envvar=None):
        self.dest = dest
        self.options = options
        self.required = required
        self.type = _convert_type(type, default=default)
        self.default = self.type(default)
        self.help = help
        if short_help is None and help:
            short_help = make_default_short_help(help)
        self.short_help = short_help
        self.metavar = metavar
        self.envvar = envvar

    def __reduce__(self):
        return (Parameter, self.__reduce_keys__())

    def __reduce_keys__(self):
        return (self.dest, self.options, self.type, self.required,
                self.nargs, self.default, self.help, self.short_help,
                self.metavar, self.envvar)


def _param_memo(fun, param):
    if isinstance(fun, LazyProxy):
        fun.__then__(lambda task: task.parameters.append(param))
        return
    if ITask.providedBy(fun):
        fun.parameters.append(param)
    else:
        if not hasattr(fun, '__tatoo_params__'):
            fun.__tatoo_params__ = []
        fun.__tatoo_params__.append(param)


def parameter(dest, *options, **attrs):
    """Attaches a parameter to the command. All positional arguments are
    passed as parameter declarations to :class:`Parameter`; all keyword
    arguments are forwarded unchanged (except ``cls`` and ``memoizer``).
    This is equivalent to creating an :class:`Parameter` instance manually
    and attaching it to the :attr:`Command.params` list.

    :keyword cls: the parameter class to instantiate. This defaults to
        :class:`Parameter`.

    """
    def decorator(fun):
        for name in ('help', 'short_help'):
            if name in attrs:
                attrs[name] = inspect.cleandoc(attrs[name])
        ParameterClass = attrs.pop('cls', Parameter)
        _param_memo(fun, ParameterClass(dest, options, **attrs))
        return fun
    return decorator


# pylint: skip-file
@task_prerun.connect
def validate_params(sender, request, **kwargs):
    if not sender.validate_params or not sender.parameters:
        return
    s = signature(sender)
    args, kwargs = request['args'], request['kwargs']
    bound = s.bind(*args, **kwargs)
    for param in s.parameters.values():
        if (param.name not in bound.arguments and
                param.default is not param.empty):
            bound.arguments[param.name] = param.default
    arguments = bound.arguments
    for param in reversed(sender.parameters):
        arguments[param.dest] = param.type(arguments[param.dest])
    request['args'] = bound.args
    request['kwargs'] = bound.kwargs
