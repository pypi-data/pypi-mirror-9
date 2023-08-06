#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from django.contrib import admin

from .models import CarouselPlugin


class CarouselPluginAdmin(admin.ModelAdmin):
    pass
admin.site.register(CarouselPlugin, CarouselPluginAdmin)
