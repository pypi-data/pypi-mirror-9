# -*- coding: utf-8 -*-
"""

    tatoo.utils.text
    ~~~~~~~~~~~~~~~~~

    Utilities to work with text.

"""

from __future__ import absolute_import, unicode_literals

from six import string_types

from pprint import pformat

__all__ = ['truncate', 'pretty']


def truncate(text, maxlen=128, suffix='...'):
    """Truncates text to a maximum number of characters."""
    if len(text) >= maxlen:
        return text[:maxlen].rsplit(' ', 1)[0] + suffix
    return text


def pretty(value, width=80, nl_width=80, sep='\n', **kw):
    """Returns a pretty formatted value."""
    if isinstance(value, dict):
        return '{{{0} {1}'.format(sep, pformat(value, 4, nl_width)[1:])
    elif isinstance(value, tuple):
        return '{0}{1}{2}'.format(
            sep, ' ' * 4, pformat(value, width=nl_width, **kw),
        )
    else:
        return pformat(value, width=width, **kw)
