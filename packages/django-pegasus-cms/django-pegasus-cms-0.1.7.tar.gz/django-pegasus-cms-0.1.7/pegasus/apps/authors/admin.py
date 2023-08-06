#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from django.contrib import admin
from genericadmin.admin import GenericAdminModelAdmin

from content.admin import PromoInline

from .models import Author, Department


class DepartmentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Department, DepartmentAdmin)


class AuthorAdmin(FrontendEditableAdminMixin, GenericAdminModelAdmin):
    frontend_editable_fields = ('first_name', 'last_name', 'title', 'bio', 'image', 'email', )
    prepopulated_fields = {'slug': ('first_name', 'last_name', )}
    inlines = [PromoInline]

admin.site.register(Author, AuthorAdmin)
