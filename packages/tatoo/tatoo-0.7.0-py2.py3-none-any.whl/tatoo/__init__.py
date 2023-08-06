# -*- coding: utf-8 -*-
"""
    tatoo
    ~~~~~

    Python task toolkit.

"""

from __future__ import absolute_import, unicode_literals

from .environment import Environment
from .task.parameter import parameter
from ._version import __version__, __author__, __contact__  # noqa

__all__ = ['Environment', 'parameter']
