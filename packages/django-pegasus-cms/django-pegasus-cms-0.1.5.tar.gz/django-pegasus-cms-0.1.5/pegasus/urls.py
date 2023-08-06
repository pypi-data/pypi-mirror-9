#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls import *
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from authors.views import AuthorDetail, AuthorList
from .sitemaps import (ArticleSitemap, AuthorSitemap, CaseSitemap,
                       EventSitemap, IssueSitemap, TopicSitemap)

from pegasus import views

admin.autodiscover()

sitemaps = {
    'cmspages': CMSSitemap,
    'authors': AuthorSitemap,
    'articles': ArticleSitemap,
    'topics': TopicSitemap,
    'issues': IssueSitemap,
    'events': EventSitemap,
    'cases': CaseSitemap
}

#urlpatterns = i18n_patterns('',
urlpatterns = patterns('',
    url(r'^404/', views.error404, name='404'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': sitemaps}),
    url(r'^authors/', include('authors.urls')),
    url(r'^', include('cms.urls')),
)

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        ) + staticfiles_urlpatterns() + urlpatterns

handler404 = 'pegasus.views.redirect404'
