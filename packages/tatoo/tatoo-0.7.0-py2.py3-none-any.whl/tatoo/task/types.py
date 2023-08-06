# -*- coding: utf-8 -*-
"""

    tatoo.task.types
    ~~~~~~~~~~~~~~~~

    Parameter types.

"""

import os
import stat
from copy import deepcopy
from uuid import UUID as _UUID

try:
    from six import string_types, text_type, binary_type
except ImportError:  # pragma: no cover
    import sys
    if sys.version_info[0] == 2:
        string_types = (basestring,)  # noqa
        binary_type = str
        text_type = unicode  # noqa
    else:
        string_types = (str,)
        binary_type = bytes
        text_type = str

__all__ = [
    'Unprocessed', 'String', 'Bool', 'Int', 'Float', 'UUID',
    'Choice', 'CaseInsensitiveChoice', 'IntRange', 'Path',
]


def safe_str(obj, coding='utf-8'):
    if isinstance(obj, binary_type):
        return obj.decode(coding)
    return text_type(obj)


class ParameterType(object):
    """Base class for parameter types."""

    #: Type name.
    name = None

    def __call__(self, value, *args, **kwargs):
        """Convert the string value to the appropriate type.
        This method must be idempotent, so multiple conversions of the same
        value must return the unchaged object.
        Note that :const:`None` values are not converted.
        """
        if value is not None:
            return self._convert(value, *args, **kwargs)

    def get_metavar(self, param):  # pragma: no cover
        """Returns the metavar default for this param, if provided."""

    def get_missing_message(self, param):  # pragma: no cover
        """Optionally might return extra information
        about a missing parameter."""

    def _convert(self, value, *args, **kwargs):
        return value

    def __deepcopy__(self, memo):
        # Parameter types must be deepcopy-able
        cls = self.__class__
        copy = cls.__new__(cls)
        memo[id(self)] = copy
        for k, v in self.__dict__.items():
            setattr(copy, k, deepcopy(v))
        return copy

    def __reduce__(self):
        return (self.__class__, self.__reduce_args__(), {'name': self.name})

    def __reduce_args__(self):
        return ()


class UnprocessedType(ParameterType):
    """Returns original unprocessed value."""
    name = ''

Unprocessed = UnprocessedType()


class StringType(ParameterType):
    """Converts value to string."""
    name = 'String'

    def _convert(self, value, *args, **kwargs):
        return safe_str(value)

String = StringType()


class Choice(ParameterType):
    """The choice type allows a value to be checked against a fixed set of
    supported values.

    :param choices: List of valid choices.
    :keyword type: If specified, each choice element and processing value
        will be casted to this type. By default the type is
        :ref:`Unprocessed`, which means that you can pass arbitrary objects.
    """

    name = 'Choice'

    def __init__(self, choices, item_type=Unprocessed, *args, **kwargs):
        super(Choice, self).__init__(*args, **kwargs)
        self.choices = [item_type(choice) for choice in choices]
        self.item_type = item_type

    def _convert(self, value, *args, **kwargs):
        value = self.item_type(value)
        if value in self.choices:
            return value
        raise ValueError('invalid choice {0!r}'.format(value))

    def get_metavar(self, param):  # pragma: no cover
        return '[{0}]'.format('|'.join(self.choices))

    def get_missing_message(self, param):  # pragma: no cover
        return 'Choose from {0}'.format('|'.join(self.choices))

    def __reduce_args__(self):
        return (self.choices, self.item_type)


class CaseInsensitiveChoice(Choice):
    """Similarly to the choice type, this type allows a value
    to be checked regardless of the case.

    Note that this type works only with strings.
    """

    def __init__(self, choices):
        super(CaseInsensitiveChoice, self).__init__(())
        self.choices = [(String(choice)).lower() for choice in choices]
        self.item_type = String

    def _convert(self, value, *args, **kwargs):
        value = self.item_type(value)
        if value.lower() in self.choices:
            return value
        raise ValueError('invalid choice {0!r}'.format(value))

    def __reduce_args__(self):
        return (self.choices,)


def strtobool(term, table={'false': False, 'no': False, 'n': False, '0': False,
                           'true': True, 'yes': True, 'y': True, '1': True,
                           'on': True, 'off': False}):
    """Convert common terms for true/false to bool
    (true/false/yes/no/on/off/1/0)."""
    # pylint: disable=W0102
    if isinstance(term, string_types):
        try:
            return table[term.lower()]
        except KeyError:
            raise ValueError('Cannot coerce {0!r} to type bool'.format(term))
    return term


class BoolType(ParameterType):
    """Converts value to boolean."""
    name = 'Bool'

    def _convert(self, value, *args, **kwargs):
        return strtobool(value)

Bool = BoolType()


class IntType(ParameterType):
    """Converts value to int."""
    name = 'Int'

    def _convert(self, value, *args, **kwargs):
        return int(value)

Int = IntType()


class FloatType(ParameterType):
    """Converts value to float."""
    name = 'Float'

    def _convert(self, value, *args, **kwargs):
        return float(value)

Float = FloatType()


class IntRange(ParameterType):
    """A parameter that works similar to :class:`INT` but restricts
    the value to fit into a range.  The default behavior is to fail if the
    value falls outside the range, but it can also be silently clamped
    between the two edges.
    """
    name = 'IntRange'

    def __init__(self, low=None, high=None, clamp=False, *args, **kwargs):
        super(IntRange, self).__init__(*args, **kwargs)
        self.low, self.high, self.clamp = Int(low), Int(high), clamp

    def _convert(self, value, *args, **kwargs):
        value = Int(value)
        if self.clamp:
            if self.low is not None and value < self.low:
                return self.low
            if self.high is not None and value > self.high:
                return self.high
        if (self.low is not None and value < self.low or
                self.high is not None and value > self.high):
            if self.low is None:
                raise ValueError(
                    '{0} is bigger than the maximum valid value {1}.'.format(
                        value, self.high
                    )
                )
            elif self.high is None:
                raise ValueError(
                    '{0} is smaller than the minimum valid value {1}.'.format(
                        value, self.low
                    )
                )
            else:
                raise ValueError(
                    '{0} is not in the valid range of {1} to {2}.'.format(
                        value, self.low, self.high
                    )
                )
        return value

    def get_metavar(self, param):  # pragma: no cover
        left = '(-inf' if self.low is None else '[{0}'.format(self.low)
        right = 'inf)' if self.high is None else '{0}]'.format(self.high)
        return '{0}..{1}'.format(left, right)

    def get_missing_message(self, param):  # pragma: no cover
        left = '(-inf' if self.low is None else '[{0}'.format(self.low)
        right = 'inf)' if self.high is None else '{0}]'.format(self.high)
        interval = '{0}..{1}'.format(left, right)
        return 'Select an integer in {0}'.format(interval)

    def __reduce_args__(self):
        return (self.low, self.high, self.clamp)


class UUIDType(ParameterType):
    """Converts value to UUID."""
    name = 'UUID'

    def _convert(self, value, *args, **kwargs):
        return _UUID(value)

UUID = UUIDType()


class Path(ParameterType):
    """The path type. It performs various basic checks about what the file
    or directory should be and returns the path if all checks are passed.

    :param exists: if set to true, the file or directory needs to exist for
                   this value to be valid. If this is not required and a
                   file does indeed not exist, then all further checks are
                   silently skipped.
    :param file_okay: controls if a file is a possible value.
    :param dir_okay: controls if a directory is a possible value.
    :param writable: if true, a writable check is performed.
    :param readable: if true, a readable check is performed.
    :param resolve_path: if this is true, then the path is fully resolved
                         before the value is passed onwards. This means
                         that it's absolute and symlinks are resolved.
    """

    def __init__(self, exists=False, file_okay=True, dir_okay=True,
                 writable=False, readable=True, resolve_path=False,
                 *args, **kwargs):
        super(Path, self).__init__(*args, **kwargs)

        self.file_okay = file_okay
        self.dir_okay = dir_okay
        self.writable = writable
        self.readable = readable
        self.exists = exists
        self.resolve_path = resolve_path

    def _convert(self, value, *args, **kwargs):
        orig = value
        if self.resolve_path:
            value = os.path.realpath(value)

        try:
            fstat = os.stat(value)
        except OSError:
            if not self.exists:
                return value
            raise

        orig = safe_str(orig)
        if not self.file_okay and stat.S_ISREG(fstat.st_mode):
            raise ValueError('{0} "{1}" is a file.'.format(
                self.path_type, orig
            ))
        if not self.dir_okay and stat.S_ISDIR(fstat.st_mode):
            raise ValueError('{0} "{1}" is a directory.'.format(
                self.path_type, orig
            ))
        if self.writable and not os.access(value, os.W_OK):
            raise ValueError('{0} "{1}" is not writable.'.format(
                self.path_type, orig
            ))
        if self.readable and not os.access(value, os.R_OK):
            raise ValueError('{0} "{1}" is not readable.'.format(
                self.path_type, orig
            ))
        return value

    @property
    def path_type(self):
        path_type = 'Path'
        if self.file_okay and not self.dir_okay:
            path_type = 'File'
        if self.dir_okay and not self.file_okay:
            path_type = 'Directory'
        return path_type
    name = path_type

    def __reduce_args__(self):
        return (self.exists, self.file_okay, self.dir_okay,
                self.writable, self.readable, self.resolve_path)


def _convert_type(type_, default=None, autotype=Unprocessed):
    """Converts a callable or python type into the most appropriate param
    type.
    """
    if isinstance(type_, ParameterType):
        return type_
    guessed_type = False
    if type_ is None and default is None:
        return autotype
    if type_ is None and default is not None:
        type_ = type(default)
        guessed_type = True
    if isinstance(type_, string_types):
        return String
    if type_ is int:
        return Int
    if type_ is bool and not guessed_type:
        return Bool
    if type_ is float:
        return Float
    if guessed_type:
        return autotype
    raise RuntimeError(
        'Cannot automatically convert {0!r} type.'.format(type_)
    )
