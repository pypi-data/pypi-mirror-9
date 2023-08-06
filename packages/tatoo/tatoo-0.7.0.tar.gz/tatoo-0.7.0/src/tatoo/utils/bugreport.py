# -*- coding: utf-8 -*-
"""

    tatoo.utils.bugreport
    ~~~~~~~~~~~~~~~~~~~~~

    Utilities to help sending bug reports.

"""

from __future__ import absolute_import, unicode_literals

import sys
import platform
from tatoo._version import __version__

__all__ = ['bugreport']


PY_VERSION = platform.python_version()

BUGREPORT_INFO = """\
software ->
  tatoo: {tatoo_v} py: {py_v}

platform ->
  system: {system} arch: {arch} imp: {py_i}

settings ->
{human_settings}
"""


def pyimplementation():  # pragma: no cover
    """Return string identifying the python implementation used."""
    if hasattr(platform, 'python_implementation'):
        return platform.python_implementation()
    elif sys.platform.startswith('java'):
        return 'Jython ' + sys.platform
    elif hasattr(sys, 'pypy_version_info'):
        # pylint: disable=E1101
        v = '.'.join(str(p) for p in sys.pypy_version_info[:3])
        if sys.pypy_version_info[3:]:
            v += '-' + ''.join(str(p) for p in sys.pypy_version_info[3:])
        return 'PyPy ' + v
    else:
        return 'CPython'


def bugreport(env):
    """Return a string containing information useful in bug reports."""
    return BUGREPORT_INFO.format(
        system=platform.system(),
        arch=', '.join(x for x in platform.architecture() if x),
        py_i=pyimplementation(),
        tatoo_v=__version__,
        py_v=PY_VERSION,
        human_settings=env.settings.humanize(),
    )
