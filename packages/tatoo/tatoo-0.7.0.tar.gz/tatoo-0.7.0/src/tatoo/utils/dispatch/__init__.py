# -*- coding: utf-8 -*-
"""

    tatoo.utils.dispatch
    ~~~~~~~~~~~~~~~~~~~~

    Multiple-producer-multiple-consumer signal registration.

"""

from __future__ import absolute_import, unicode_literals

# Code taken from django.dispatch
from .dispatch import Signal, receiver

__all__ = ['Signal', 'receiver']
