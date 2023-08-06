#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.toolbar_pool import toolbar_pool
from pegasus.cms_toolbar import CelerityExtensionToolbar

from .models import LeftNavExtension


@toolbar_pool.register
class LeftNavExtensionToolbar(CelerityExtensionToolbar):
    extension_model = LeftNavExtension
