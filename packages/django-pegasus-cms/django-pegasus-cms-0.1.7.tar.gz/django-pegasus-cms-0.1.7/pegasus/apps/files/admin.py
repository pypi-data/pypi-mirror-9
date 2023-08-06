#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from django.contrib import admin

from .models import File


class FileAdmin(admin.ModelAdmin):
    list_display = ('name', 'url',)
    readonly_fields = ('name', 'url',)
    fieldsets = (
        (None, {
            'fields': ('file', 'name', 'url',)
        }),
    )
admin.site.register(File, FileAdmin)
