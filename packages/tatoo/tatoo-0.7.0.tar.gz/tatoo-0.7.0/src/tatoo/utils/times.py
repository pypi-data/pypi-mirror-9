# -*- coding: utf-8 -*-
"""

    tatoo.utils.times
    ~~~~~~~~~~~~~~~~~~

    Time-related utilities.

"""

# pylint: skip-file
from __future__ import absolute_import, unicode_literals

__all__ = ['monotonic']

try:
    from time import monotonic
except ImportError:  # pragma: no cover
    monotonic = None


##############################################################################
# Code mostly stolen from trollius/time_utils.py
# Backport of time.monotonic() of Python 3.3 (PEP 418) for Python 2.6 and 2.7.
#
# Unlike the original module,
# - time_monotonic() is renamed to monotonic() and it will not fall back
#   to a non-monotonic implementation if any error occurs, you should manually
#   specify a fallback function.
# - time_monotonic_resolution is renamed to monotonic_resolution
#
# Support Windows, Mac OS X, Linux, FreeBSD, OpenBSD and Solaris, but requires
# the ctypes module.
##############################################################################
if monotonic is None:  # pragma: no cover
    import os
    import sys

    if os.name == "nt":
        # Windows: use GetTickCount64() or GetTickCount()
        import ctypes
        from ctypes import windll
        from ctypes.wintypes import DWORD
        # GetTickCount64() requires Windows Vista, Server 2008 or later
        if hasattr(windll.kernel32, 'GetTickCount64'):
            ULONGLONG = ctypes.c_uint64

            GetTickCount64 = windll.kernel32.GetTickCount64
            GetTickCount64.restype = ULONGLONG
            GetTickCount64.argtypes = ()

            def monotonic():
                return GetTickCount64() * 1e-3
            monotonic_resolution = 1e-3
        else:
            GetTickCount = windll.kernel32.GetTickCount
            GetTickCount.restype = DWORD
            GetTickCount.argtypes = ()

            # Detect GetTickCount() integer overflow (32 bits, roll-over after
            # 49.7 days). It increases an internal epoch (reference time) by
            # 2^32 each time that an overflow is detected. The epoch is stored
            # in the process-local state and so the value of monotonic() may be
            # different in two Python processes running for more than 49 days.
            def monotonic():
                ticks = GetTickCount()
                if ticks < monotonic.last:
                    # Integer overflow detected
                    monotonic.delta += 2**32
                monotonic.last = ticks
                return (ticks + monotonic.delta) * 1e-3
            monotonic.last = 0
            monotonic.delta = 0
            monotonic_resolution = 1e-3

    elif sys.platform == 'darwin':
        # Mac OS X: use mach_absolute_time() and mach_timebase_info()
        import ctypes
        import ctypes.util
        libc_name = ctypes.util.find_library('c')
        libc = ctypes.CDLL(libc_name, use_errno=True)

        mach_absolute_time = libc.mach_absolute_time
        mach_absolute_time.argtypes = ()
        mach_absolute_time.restype = ctypes.c_uint64

        class mach_timebase_info_data_t(ctypes.Structure):
            _fields_ = (
                ('numer', ctypes.c_uint32),
                ('denom', ctypes.c_uint32),
            )
        mach_timebase_info_data_p = ctypes.POINTER(mach_timebase_info_data_t)

        mach_timebase_info = libc.mach_timebase_info
        mach_timebase_info.argtypes = (mach_timebase_info_data_p,)
        mach_timebase_info.restype = ctypes.c_int

        def monotonic():
            return mach_absolute_time() * monotonic.factor

        timebase = mach_timebase_info_data_t()
        mach_timebase_info(ctypes.byref(timebase))
        monotonic.factor = float(timebase.numer) / timebase.denom * 1e-9
        monotonic_resolution = monotonic.factor
        del timebase

    elif sys.platform.startswith(("linux", "freebsd", "openbsd", "sunos")):
        # Linux, FreeBSD, OpenBSD: use clock_gettime(CLOCK_MONOTONIC)
        # Solaris: use clock_gettime(CLOCK_HIGHRES)
        import ctypes
        import ctypes.util

        if sys.platform.startswith(("freebsd", "openbsd")):
            libraries = ('c',)
        elif sys.platform.startswith("linux"):
            # Linux: in glibc 2.17+, clock_gettime() is provided by the libc,
            # on older versions, it is provided by librt
            libraries = ('c', 'rt')
        else:
            # Solaris
            libraries = ('rt',)

        library = None
        for name in libraries:
            filename = ctypes.util.find_library(name)
            if not filename:
                continue
            library = ctypes.CDLL(filename, use_errno=True)
            if not hasattr(library, 'clock_gettime'):
                library = None

        if library is not None:
            if sys.platform.startswith("openbsd"):
                import platform
                release = platform.release()
                release = tuple(map(int, release.split('.')))
                if release >= (5, 5):
                    time_t = ctypes.c_int64
                else:
                    time_t = ctypes.c_int32
            else:
                time_t = ctypes.c_long
            clockid_t = ctypes.c_int

            class timespec(ctypes.Structure):
                _fields_ = (
                    ('tv_sec', time_t),
                    ('tv_nsec', ctypes.c_long),
                )
            timespec_p = ctypes.POINTER(timespec)

            clock_gettime = library.clock_gettime
            clock_gettime.argtypes = (clockid_t, timespec_p)
            clock_gettime.restype = ctypes.c_int

            def ctypes_oserror():
                errno = ctypes.get_errno()
                message = os.strerror(errno)
                return OSError(errno, message)

            def monotonic():
                ts = timespec()
                err = clock_gettime(monotonic.clk_id, ctypes.byref(ts))
                if err:
                    raise ctypes_oserror()
                return ts.tv_sec + ts.tv_nsec * 1e-9

            if sys.platform.startswith("linux"):
                monotonic.clk_id = 1   # CLOCK_MONOTONIC
            elif sys.platform.startswith("freebsd"):
                monotonic.clk_id = 4   # CLOCK_MONOTONIC
            elif sys.platform.startswith("openbsd"):
                monotonic.clk_id = 3   # CLOCK_MONOTONIC
            else:
                assert sys.platform.startswith("sunos")
                monotonic.clk_id = 4   # CLOCK_HIGHRES

            def get_resolution():
                _clock_getres = library.clock_getres
                _clock_getres.argtypes = (clockid_t, timespec_p)
                _clock_getres.restype = ctypes.c_int

                ts = timespec()
                err = _clock_getres(monotonic.clk_id, ctypes.byref(ts))
                if err:
                    raise ctypes_oserror()
                return ts.tv_sec + ts.tv_nsec * 1e-9
            monotonic_resolution = get_resolution()
            del get_resolution
        else:
            raise ImportError
    else:
        raise ImportError
