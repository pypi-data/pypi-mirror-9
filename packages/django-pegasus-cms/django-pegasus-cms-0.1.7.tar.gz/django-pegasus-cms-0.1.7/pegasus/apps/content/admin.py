#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.admin.placeholderadmin import FrontendEditableAdminMixin
from django.contrib import admin
from genericadmin.admin import GenericAdminModelAdmin, GenericTabularInline

from .models import (Article, ArticleType, Case, Event, Issue, LegalTeam,
                     Promo, PromoPlacement, Topic)


class CelerityContentNodeAdminMixin(FrontendEditableAdminMixin):
    list_display = ('headline', 'featured', 'priority',)
    frontend_editable_fields = ('headline', 'featured', 'priority',)
    readonly_fields = ('slug',)
    search_fields = ('headline', 'slug',)
    ordering = ('headline',)
    list_per_page = 50

    fieldsets = (
        ('Curation', {
            'fields': ('featured', 'priority',)
        }),
        ('Naming', {
            'fields': ('headline', 'slug',)
        }),
    )

class PromoInline(GenericTabularInline):
    model = PromoPlacement

class CelerityContentTypeAdminMixin(CelerityContentNodeAdminMixin,
                                    GenericAdminModelAdmin):
    list_display = (CelerityContentNodeAdminMixin.list_display[0],) +\
                   ('article_type', 'issue', 'author',) +\
                   CelerityContentNodeAdminMixin.list_display[1:]
    list_filter = ('article_type', 'issues', 'author',)

    inlines = [PromoInline]

    frontend_editable_fields = CelerityContentNodeAdminMixin\
        .frontend_editable_fields + ('body',)

    search_fields = CelerityContentNodeAdminMixin.search_fields +\
                    ('keywords__name', 'author__first_name',
                     'author__last_name',)

    filter_horizontal = ('issues',)
    ordering = ('-featured', 'priority', '-date_published',)

    fieldsets = CelerityContentNodeAdminMixin.fieldsets + (
        ('Classification', {
            'fields': ('article_type', 'issues', 'keywords',)
        }),
    )


class IssueAdmin(CelerityContentNodeAdminMixin, admin.ModelAdmin):
    list_display = (CelerityContentNodeAdminMixin.list_display[0],) +\
                   ('topic',) +\
                   CelerityContentNodeAdminMixin.list_display[1:]
    list_filter = ('topic',)
    search_fields = CelerityContentNodeAdminMixin.search_fields +\
                    ('topic__headline',)
    ordering = ('topic__headline', 'headline',)

    fieldsets = (
        CelerityContentNodeAdminMixin.fieldsets[0],
        (None, {
            'fields': ('topic',),
        }),
        CelerityContentNodeAdminMixin.fieldsets[1],
    )
admin.site.register(Issue, IssueAdmin)

class IssuesInline(admin.TabularInline):
    model = Issue
    fields = CelerityContentNodeAdminMixin.list_display
    extra = 1

class TopicAdmin(CelerityContentNodeAdminMixin, admin.ModelAdmin):
    inlines = [IssuesInline]
admin.site.register(Topic, TopicAdmin)

class ArticleAdmin(CelerityContentTypeAdminMixin, admin.ModelAdmin):
    search_fields = CelerityContentTypeAdminMixin.search_fields +\
                    ('subheading', 'lead',)
    fieldsets = (
        CelerityContentTypeAdminMixin.fieldsets[0],
        CelerityContentTypeAdminMixin.fieldsets[1],
        CelerityContentTypeAdminMixin.fieldsets[2],
        ('Images', {
            'fields': ('image_lead', 'image_lead_alt_text',)
        }),
        ('Additional Settings', {
            'fields': ('subheading', 'lead')
        }),
        ('Publishing', {
            'fields': ('author', 'date_label', 'date_published', 'source',
                       'show_comments',),
        }),
    )
admin.site.register(Article, ArticleAdmin)

class EventAdmin(CelerityContentTypeAdminMixin, admin.ModelAdmin):
    fieldsets = CelerityContentTypeAdminMixin.fieldsets +\
        (
            ('Event Details', {
                'fields': ('title', 'event_image', 'event_image_alt_text',
                           'event_url', 'url_label', 'fee', 'location_info',
                           'event_date',)
            }),
            ('Publishing', {
                'fields': ('author', 'date_published',),
            }),
        )
admin.site.register(Event, EventAdmin)


class LegalTeamInline(admin.TabularInline):
    model = LegalTeam
    extra = 3
    fields = ('author', 'bio',)
    verbose_name = 'Legal Team'

class CaseAdmin(CelerityContentTypeAdminMixin, admin.ModelAdmin):
    inlines = [LegalTeamInline] + CelerityContentTypeAdminMixin.inlines
    search_fields = CelerityContentTypeAdminMixin.search_fields +\
                    ('subheading', 'lead',)
    frontend_editable_fields = CelerityContentTypeAdminMixin\
        .frontend_editable_fields + ('subheading',
                                     'lead',
                                     'last_step',
                                     'next_step',)

    fieldsets = (
        CelerityContentTypeAdminMixin.fieldsets[0],
        CelerityContentTypeAdminMixin.fieldsets[1],
        CelerityContentTypeAdminMixin.fieldsets[2],
        ('Images', {
            'fields': ('image_lead', 'image_lead_alt_text',)
        }),
        ('Additional Settings', {
            'fields': ('subheading', 'lead')
        }),
        ('Navigation', {
            'fields': ('last_step', 'next_step',),
        }),
        ('Publishing', {
            'fields': ('author', 'date_label', 'date_published', 'source',
                       'show_comments',),
        }),
    )
admin.site.register(Case, CaseAdmin)

class PromoAdmin(admin.ModelAdmin):
    inlines = [PromoInline]
admin.site.register(Promo, PromoAdmin)

class PromoPlacementAdmin(GenericAdminModelAdmin):
    content_type_whitelist = ('authors/author',
                              'cms/page',
                              'content/article',
                              'content/case',
                              'content/event',)
admin.site.register(PromoPlacement, PromoPlacementAdmin)

class ArticleTypeAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)
admin.site.register(ArticleType, ArticleTypeAdmin)
