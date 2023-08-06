# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .constants import MAX_PREFIX_LENGTH

SETTINGS_PREFIX = 'DD_SESSION'


def get(key, default):
    return getattr(settings, '_'.join([SETTINGS_PREFIX, key]), default)

PREFIX = get('PREFIX', 'default')                      # prefix for data keys
INFO_TIMEOUT = get('INFO_TIMEOUT', 60 * 60 * 24)       # timeout of keeping info existence key
INFO_PREFIX = get('INFO_PREFIX', PREFIX)               # prefix for info existence keys
USE_FALLBACK = get('USE_FALLBACK', True)               # use read-only fallback to database sessions

if len(PREFIX) > MAX_PREFIX_LENGTH:
    raise ImproperlyConfigured('Prefix %s is more that MAX_PREFIX_LENGTH %s' % (PREFIX, MAX_PREFIX_LENGTH))