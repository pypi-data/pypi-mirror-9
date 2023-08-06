# -*- coding: utf-8 -*-
"""

    tatoo.interfaces
    ~~~~~~~~~~~~~~~~

    All interfaces defined in tatoo.

"""

# pragma: no cover
# pylint: skip-file
from __future__ import absolute_import, unicode_literals

from zope.interface import Interface
from zope.interface import Attribute
from zope.interface.interfaces import IComponents
from zope.interface.common.mapping import IFullMapping


# General-purpose interfaces

class IEnvironment(IComponents):  # pragma: no cover
    """Tatoo environment interface."""

    name = Attribute('Environment name.')
    tasks = Attribute("""\
        Convinient way to access the mapping of registered tasks.
        The other way is to call :meth:`getUtility` with :class:`ITaskManager`.
    """)
    settings = Attribute("""\
        Convinient method to access the mapping of settings.
        The other way is calling :meth:`getUtility` with :class:`ISettings`.
    """)
    logger = Attribute("""\
        Convinient method to access the logger wrapper instance.
        The other way is calling :meth:`getUtility` with :class:`ILogger`.
    """)
    extensions = Attribute("""\
        Convinient method to access the mapping of extensions.
        The other way is calling :meth:`getUtility` with
        :class:`IExtensionManager`.
    """)

    def task(*args, **kwargs):
        """Decorator to create and bind tasks to the env."""

    def bugreport():
        """Returns bugreport information."""

    def subclass_with_self(cls, name=None, attr='env', reverse_name=None,
                           **kwargs):
        """Subclass an env-compatible class by settring its ``attr`` attribute
        to be this env instance.

        Env-compatible means that the class has an attribute that provides
        the default env it should use, e.g.::

            class Foo:
                env = None

        :param cls: The env-compatible class to subclass.
        :keyword name: Custom name for the target class.
        :keyword attr: Name of the attribute holding the app, default is
            ``env``.
        """


class IManager(IFullMapping):
    """Mapping interface to managed objects."""

    env = Attribute('Environment instance.')
    interface = Attribute('Interface which managed objects should implement.')
    strict = Attribute("""\
        If :const:`True`, the manager will refuse attempts to register
        an object which has already registered name.
    """)


class ILogger(Interface):  # pragma: no cover
    """Convinience logging wrapper."""

    env = Attribute('Environment instance.')

    def setup(mapping=None, force=False):
        """Setup logging subsystem. Tatoo will take the configuration
        to prepare logging by itself, however, you can manually
        call this method with a custom dictionary configuration.
        In this case, env configuration is ignored.
        """

    def get_logger(name):
        """Returns a general purpose logger instance."""

    def get_task_logger(name):
        """Returns a logger instance suitable for logging within tasks."""

    def get_extension_logger(name, extension):
        """Returns a logger instance suitable for logging
        within extensions.
        """


class ISettings(IFullMapping):  # pragma: no cover
    """Interface for configuration container."""

    def add_defaults(mapping):
        """Add default values from mapping."""

    def without_defaults():
        """Return the current settings, but without defaults."""

    def table(with_defaults=False, censored=True):
        """Returns a censored configuration dictionary."""

    def humanize(with_defaults=False, censored=True):
        """Return a human readable string showing changes
        to the configuration.
        """


# Task-related interfaces

class ITask(Interface):  # pragma: no cover
    """Task class that can be created from any callable."""

    env = Attribute('Environment instance.')
    name = Attribute('Name of the task')
    internal = Attribute("""\
        Internal tasks are not shown when listing the task registry.
    """)
    throws = Attribute("""
        Tuple of expected exceptions which may be raised
        during task execution. The task result will not be set
        to "ERROR", but the message about thrown exception
        will be logged.
    """)
    request = Attribute('Task execution request.')
    manager = Attribute('Instance of :class:`ITaskManager` implementer.')
    parameters = Attribute("""\
        Optional list of parameters.
        Note that parameters will appear in reversed order.
    """)
    validate_params = Attribute("""\
        If :const:`True`, passed arguments will be validated using
        :attr:`params`.
    """)

    def __call__(*args, **kwargs):
        """Wrapped callable's body."""

    def apply(args=None, kwargs=None, **request):
        """Trace task execution capturing state changes and logging.

        :keyword args: Positional arguments.
        :type args: list or tuple

        :keyword kwargs: Keyword arguments.
        :type kwargs: mapping

        :param \*\*request: Execution request (xxx document).

        :retval: Instance of :class:`~tatoo.result.EagerResult` class.

        """


class ITaskManager(IManager):  # pragma: no cover
    """Mapping interface to managed tasks."""

    tracer = Attribute('Instance of :class:`ITracer` implementer.')

    def task_from_fun(fun, name=None, base=None, bind=False, **opts):
        """Creates task object from the callable."""

    def gen_task_name(fun, extension=None):
        """Generates task name."""


class ITracer(Interface):  # pragma: no cover
    """Task execution tracer interface."""

    env = Attribute('Environment instance.')

    def build_tracer(task):
        """Return a function that traces task execution, catches all exceptions
        and updates result backends with the state and the result.

        If the call was successful, it saves the result to the task result
        backends and sets the task state to `"SUCCESS"`.

        If the call rasies :exc:`~@Retry`, it extracts the original exception,
        uses that as result and sets the task state to `"RETRY"`.

        If the call results in an exception, it saves the exception as the task
        result, and sets the task state to `"FAILURE"`.
        """


class IResultHandler(Interface):  # pragma: no cover
    """Task execution handlers."""

    log_format = Attribute('Logging mesage format.')
    severity = Attribute('Logging severity.')
    exc_info = Attribute("""\
            Defines whether to include the exception info to the log message.
    """)

    def __call__(task, request, retval, runtime):
        """Handle the execution result."""


class ITaskResult(Interface):  # pragma: no cover
    """Convinient wrapper around the result of a task execution."""

    request_id = Attribute('Request id.')
    result = Attribute("""\
        When the task has been executed, this contains the returned
        value. If the task raised an exception, this will be
        the exception instance.
    """)
    traceback = Attribute(
        'If the task raised an exception, this contains the traceback.'
    )
    state = Attribute('The current state of the task request.')
    runtime = Attribute('The execution time.')

    def get(propagate=True):
        """Wait until the task is ready and return its result."""

    def ready():
        """Returns :const:`True` if the task has been executed."""

    def successful():
        """Returns :const:`True` if the task executed successfully."""

    def failed(self):
        """Returns :const:`True` if the task failed."""


# Extensions-related interfaces

class IExtension(Interface):  # pragma: no cover
    """Tatoo extension."""

    env = Attribute('Environment instance.')
    name = Attribute('Extension name.')
    alias = Attribute('Short extension name.')
    enabled = Attribute('Defines whether this extension is enabled.')
    version = Attribute('Extension version')
    manager = Attribute('Instance of :class:`IExtensionManager` implementer.')

    def task(*args, **kwargs):
        """Decorator to create and bind tasks to the extension."""


class IExtensionManager(IManager):  # pragma: no cover
    """Mapping interface to managed extensions."""

    def load_from_entry_points():
        """Loads extensions from "tatoo.extensions" entry points."""
