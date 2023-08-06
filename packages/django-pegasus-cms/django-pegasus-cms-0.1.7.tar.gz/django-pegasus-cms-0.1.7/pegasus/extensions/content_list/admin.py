#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.extensions import PageExtensionAdmin
from django import forms
from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from .models import ContentList, ContentListExtension


class ContentListInline(admin.TabularInline):
    model = ContentList
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple,},
    }
    extra = 0

class ContentListExtensionAdmin(PageExtensionAdmin):
    inlines = (ContentListInline,)
admin.site.register(ContentListExtension, ContentListExtensionAdmin)
