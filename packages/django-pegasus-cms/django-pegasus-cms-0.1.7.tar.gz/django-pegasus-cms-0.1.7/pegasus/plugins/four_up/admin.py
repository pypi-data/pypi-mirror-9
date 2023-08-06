#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.admin.placeholderadmin import PlaceholderAdminMixin
from django.contrib import admin

from .models import FourUpPlugin


class FourUpPluginAdmin(PlaceholderAdminMixin, admin.ModelAdmin):
    class Media:
        js = ('//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js',
              'js/4up-admin.js',)
admin.site.register(FourUpPlugin, FourUpPluginAdmin)
