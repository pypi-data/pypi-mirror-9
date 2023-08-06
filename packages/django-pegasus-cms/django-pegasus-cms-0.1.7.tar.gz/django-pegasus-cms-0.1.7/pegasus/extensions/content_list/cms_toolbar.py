#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.toolbar_pool import toolbar_pool
from pegasus.cms_toolbar import CelerityExtensionToolbar

from .models import ContentListExtension


@toolbar_pool.register
class ContentListExtensionToolbar(CelerityExtensionToolbar):
    extension_model = ContentListExtension
