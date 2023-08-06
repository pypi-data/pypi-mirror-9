#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from .base import *

INSTALLED_APPS += ('debug_toolbar',)

PRECOMPRESSED_SETTINGS = {
    'GZIP_PATTERNS': (),
}

try:
    from .local_settings import *
except:
    pass
