# -*- coding: utf-8 -*-
"""

    tatoo.signals
    ~~~~~~~~~~~~~

    Django-like signals implementing Observer pattern.

    Functions (handlers) can be connected to these signals,
    and connected functions are called whenever a signal is received.

"""

from __future__ import absolute_import, unicode_literals

from tatoo.utils.dispatch import Signal

__all__ = [
    'task_prerun', 'task_postrun', 'task_success',
]


#: Sent before a task instance is created.
before_task_create = Signal(('name', 'fun', 'opts'))
#: Sent when the task is ready to run.
task_prerun = Signal(('request',))
#: Sent when the task just finished.
task_postrun = Signal(('retval', 'state', 'request'))
#: Sent if the task execution was successful.
task_success = Signal(('retval', 'request'))
#: Sent if the task execution fails.
task_failure = Signal(('request', 'exception', 'traceback', 'einfo'))
#: Sent on cleaning up after the task execution.
task_cleanup = Signal()
#: Sent before the looging system sets up.
before_setup_logging = Signal(('mapping',))
#: Sent when an extension is loaded.
extension_load = Signal()
