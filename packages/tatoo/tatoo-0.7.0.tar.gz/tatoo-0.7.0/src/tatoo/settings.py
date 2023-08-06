# -*- coding: utf-8 -*-
"""

    tatoo.settings
    ~~~~~~~~~~~~~~~

    Environment settings storage implementation.

"""

from __future__ import absolute_import, unicode_literals

import re
from collections import Mapping

from six import iteritems, string_types

from zope.interface import implementer

from tatoo.utils import inherit_docs
from tatoo.utils.text import pretty
from tatoo.interfaces import ISettings
from tatoo.utils.datastructures import ConfigurationView

__all__ = ['Settings']


@inherit_docs
@implementer(ISettings)
class Settings(ConfigurationView):
    """Container for configuration values."""

    DEFAULT_SETTINGS = {
        'TATOO_LOG_LEVEL': None,
        'TATOO_LOG_FILE': None,
        'TATOO_LOG_FORMAT':
            '[%(asctime)s: %(levelname)s | env: %(envname)s] %(message)s',
        'TATOO_VALIDATE_PARAMS': True,
    }

    HIDDEN_SETTINGS = re.compile(
        'API|TOKEN|KEY|SECRET|PASS|SIGNATURE|DATABASE',
        re.IGNORECASE,
    )

    def __init__(self, changes=None, defaults=None):
        dflts = self.DEFAULT_SETTINGS
        if defaults is not None:
            dflts.update(defaults)
        super(Settings, self).__init__(changes=changes or {}, defaults=dflts)

    def without_defaults(self):
        return Settings(self.changes, {})

    def table(self, with_defaults=False, censored=True):
        filt = _filter_hidden_settings if censored else lambda v, *a, **kw: v
        settings = self if with_defaults else self.without_defaults()
        return filt(dict((k, v) for k, v in iteritems(settings)
                         if k.isupper() and not k.startswith('_')),
                    self.HIDDEN_SETTINGS)

    def humanize(self, with_defaults=False, censored=True):
        return '\n'.join(
            '{0}: {1}'.format(k, pretty(v, width=79))
            for k, v in iteritems(self.table(with_defaults, censored))
        )

    def __reduce__(self):
        return (Settings, (self.changes, self.defaults))


def _maybe_censor(key, value, mask='*' * 8, HIDDEN_SETTINGS=None):
    if not HIDDEN_SETTINGS:
        return value
    if isinstance(value, Mapping):
        return _filter_hidden_settings(value, HIDDEN_SETTINGS)
    if isinstance(value, string_types):
        if HIDDEN_SETTINGS.search(key):
            return mask
    return value


def _filter_hidden_settings(settings, HIDDEN_SETTINGS=None):
    return dict((k, _maybe_censor(k, v, HIDDEN_SETTINGS=HIDDEN_SETTINGS))
                for k, v in iteritems(settings))
