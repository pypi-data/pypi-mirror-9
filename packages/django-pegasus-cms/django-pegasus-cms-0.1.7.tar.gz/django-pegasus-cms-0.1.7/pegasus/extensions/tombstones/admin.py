#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.extensions import PageExtensionAdmin
from django.contrib import admin

from .models import Highlight, TombstonesExtension


class HighlightInline(admin.TabularInline):
    model = Highlight
    extra = 4
    max_num = 4

class TombstonesExtensionAdmin(PageExtensionAdmin):
    inlines = (HighlightInline,)
admin.site.register(TombstonesExtension, TombstonesExtensionAdmin)
