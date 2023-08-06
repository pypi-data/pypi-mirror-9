#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.extensions import PageExtensionAdmin
from django.contrib import admin

from .models import LeftNavExtension


class LeftNavExtensionAdmin(PageExtensionAdmin):
    pass
admin.site.register(LeftNavExtension, LeftNavExtensionAdmin)
