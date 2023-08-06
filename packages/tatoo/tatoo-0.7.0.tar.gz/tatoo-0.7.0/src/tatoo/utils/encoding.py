# -*- coding: utf-8 -*-
"""

    tatoo.utils.encoding
    ~~~~~~~~~~~~~~~~~~~~

    Utilities to safely work with strings and bytes.

"""

# pylint: disable=W0613,E0602,W0703
from __future__ import absolute_import, unicode_literals

import sys
import traceback

from six import PY3, text_type

#: safe_str takes encoding from this file by default.
#: :func:`set_default_encoding_file` can used to set the
#: default output file.
default_encoding_file = None


def set_default_encoding_file(file):
    global default_encoding_file  # pylint: disable=W0603
    default_encoding_file = file


def get_default_encoding_file():
    return default_encoding_file


if sys.platform.startswith('java'):     # pragma: no cover

    def default_encoding(file=None):
        return 'utf-8'
else:

    def default_encoding(file=None):
        file = file or get_default_encoding_file()
        return getattr(file, 'encoding', None) or sys.getfilesystemencoding()


if PY3:

    def str_to_bytes(s):
        if isinstance(s, str):
            return s.encode()
        return s

    def bytes_to_str(s):
        if isinstance(s, bytes):
            return s.decode()
        return s

    def from_utf8(s, *args, **kwargs):
        return s

    def ensure_bytes(s):
        if not isinstance(s, bytes):
            return str_to_bytes(s)
        return s

    def default_encode(obj):
        return obj

else:  # pragma: no cover

    def str_to_bytes(s):
        if isinstance(s, unicode):  # noqa
            return s.encode()
        return s

    def bytes_to_str(s):
        return s

    def from_utf8(s, *args, **kwargs):
        return s.encode('utf-8', *args, **kwargs)

    def default_encode(obj, file=None):
        return unicode(obj, default_encoding(file))  # noqa

    ensure_bytes = str_to_bytes


def safe_str(s, errors='replace'):
    s = bytes_to_str(s)
    if not isinstance(s, (text_type, bytes)):
        return safe_repr(s, errors)
    return _safe_str(s, errors)


if PY3:

    def _safe_str(s, errors='replace', file=None):
        if isinstance(s, str):
            return s
        try:
            return str(s)
        except Exception as exc:
            return '<Unrepresentable {0!r}: {1!r} {2!r}>'.format(
                type(s), exc, '\n'.join(traceback.format_stack()))
else:  # pragma: no cover
    def _safe_str(s, errors='replace', file=None):
        encoding = default_encoding(file)
        try:
            if isinstance(s, unicode):  # noqa
                return s.encode(encoding, errors)
            return unicode(s, encoding, errors)  # noqa
        except Exception as exc:
            return '<Unrepresentable {0!r}: {1!r} {2!r}>'.format(
                type(s), exc, '\n'.join(traceback.format_stack()))


def safe_repr(o, errors='replace'):
    try:
        return repr(o)
    except Exception:
        return _safe_str(o, errors)
