# -*- coding: utf-8 -*-
"""

    tatoo.log
    ~~~~~~~~~

    Logging facilities.

"""

from __future__ import absolute_import, unicode_literals, print_function

from zope.interface import implementer

import sys
import numbers
import logging
import logging.config

from six import string_types

from tatoo.utils import inherit_docs
from tatoo.interfaces import ILogger
from tatoo.signals import before_setup_logging

__all__ = ['Logger']


# pylint: disable=F0401,W0611
# Initialize logging fallbacks
try:
    NullHandler = logging.NullHandler
except AttributeError:  # pragma: no cover
    from logutils import NullHandler
try:
    dictConfig = logging.config.dictConfig
except AttributeError:  # pragma: no cover
    from logutils.dictconfig import dictConfig
if sys.version_info < (3, 2):  # pragma: no cover
    from logutils.adapter import LoggerAdapter
else:
    LoggerAdapter = logging.LoggerAdapter
# pylint: enable=F0401,W0611

# pylint: disable=E1101,W0212
try:
    LOG_LEVELS = dict(logging._nameToLevel)
    LOG_LEVELS.update(logging._levelToName)
except AttributeError:  # pragma: no cover
    LOG_LEVELS = dict(logging._levelNames)
# pylint: enable=E1101,W0212


def get_loglevel(level):
    """Returns logging level from string or integer."""
    if level and not isinstance(level, numbers.Integral):
        return LOG_LEVELS[level.upper()]
    return level


def _get_logger(logger):
    if isinstance(logger, string_types):
        logger = logging.getLogger(logger)
    if not logger.handlers:
        logger.addHandler(NullHandler())
    return logger


def logger_isa(logger, parent):
    """Returns :const:`True` if ``parent`` is in ``logger`` parents."""
    this, seen = logger, set()
    while this:
        if this == parent:
            return True
        if this in seen:
            raise RuntimeError('Logger {0!r} parents recursive'.format(logger))
        seen.add(this)
        this = this.parent
    return False


def get_logger(name, base_logger=_get_logger('tatoo')):
    """Returns logger instance which parent is set to "tatoo" base logger."""
    log = _get_logger(name)
    if not logger_isa(log, base_logger):
        log.parent = base_logger
    return log


def get_task_logger(name, base_logger=get_logger('tatoo.task')):
    """Returns task logger instance which parent is set to
    "tatoo.task" base logger.
    """
    log = get_logger(name)
    if not logger_isa(log, base_logger):
        log.parent = base_logger
    return log


def get_extension_logger(name,
                         base_logger=get_logger('tatoo.extension')):
    """Returns extension logger instance which parent is set to
    "tatoo.extension" base logger.
    """
    log = get_logger(name)
    if not logger_isa(log, base_logger):
        log.parent = base_logger
    return log


@inherit_docs
@implementer(ILogger)
class Logger(object):
    """Logging wrapper."""

    env = None
    dictConfig = dictConfig

    def __init__(self, env=None):
        self.env = env or self.env
        self._configured = False

    def setup(self, mapping=None, force=False):
        if not self._configured or force:
            self._configured = True
            settings = self.env.settings
            before_setup_logging.send(sender=self)
            if mapping is None:
                # Prepare logging config
                tatoo = get_logger('tatoo')
                fmt = settings['TATOO_LOG_FORMAT']
                formatter = logging.Formatter(fmt)
                handler = None
                logfile = settings['TATOO_LOG_FILE']
                loglevel = settings['TATOO_LOG_LEVEL']
                if loglevel is not None:
                    level = logging.getLevelName(loglevel.upper())
                    tatoo.setLevel(level)
                    if logfile is None:
                        handler = logging.StreamHandler()
                if logfile is not None:
                    level = logging.getLevelName((loglevel or 'ERROR').upper())
                    tatoo.setLevel(level)
                    handler = logging.FileHandler(logfile, delay=True)
                if handler is not None:
                    handler.setFormatter(formatter)
                    tatoo.handlers = [handler]
            else:
                self.dictConfig(mapping)

    def get_logger(self, name):
        logger = get_logger(name)
        adapter = LoggerAdapter(logger, extra={'envname': self.env.name})
        return adapter

    def get_task_logger(self, name):
        logger = get_task_logger(name)
        adapter = LoggerAdapter(logger, extra={'envname': self.env.name})
        return adapter

    def get_extension_logger(self, name, extension):
        logger = get_extension_logger(name)
        envname = '{0}:{1}'.format(self.env.name, extension.name)
        adapter = LoggerAdapter(logger, extra={'envname': envname})
        return adapter
