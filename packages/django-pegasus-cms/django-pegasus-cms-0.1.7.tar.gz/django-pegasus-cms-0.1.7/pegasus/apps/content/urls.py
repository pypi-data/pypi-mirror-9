#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from django.conf.urls import include, patterns, url

from .views import ArticleDetail, ArticleList, CaseDetail, EventDetail

urlpatterns = patterns('',
    url(r'^(?P<topic_slug>[\w-]+)/(?P<issue_slug>[\w-]+)/case/(?P<slug>[\w-]+)/',
        CaseDetail.as_view(),
        name='case_detail'),
    url(r'^(?P<topic_slug>[\w-]+)/(?P<issue_slug>[\w-]+)/event/(?P<slug>[\w-]+)/',
        EventDetail.as_view(),
        name='event_detail'),
    url(r'^(?P<topic_slug>[\w-]+)/(?P<issue_slug>[\w-]+)/(?P<slug>[\w-]+)/',
        ArticleDetail.as_view(), name='article_detail'),
    url(r'^page/(?P<page_id>\d+)/$', ArticleList.as_view(), name='article_page_list'),
)
