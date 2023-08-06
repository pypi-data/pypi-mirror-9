#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls import include, patterns, url

from .views import AuthorDetail, AuthorList

urlpatterns = patterns('',
    url(r'^(?P<slug>[\w-]+)/$', AuthorDetail.as_view(), name='author_detail'),
    url(r'^$', AuthorList.as_view(), name='author_list'),
)
