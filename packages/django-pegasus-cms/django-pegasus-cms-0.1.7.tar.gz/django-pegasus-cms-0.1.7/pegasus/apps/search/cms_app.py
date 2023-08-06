#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

#from aldryn_search.cms_app import AldrynSearchApphook
from cms.apphook_pool import apphook_pool
from django.conf.urls import patterns, url
from django.utils.translation import ugettext_lazy as _

from .views import CeleritySearchView


#class SearchApphook(AldrynSearchApphook):
from cms.app_base import CMSApp
class SearchApphook(CMSApp):
    name = _('Search')
    urls = [patterns('',
        url('^$', CeleritySearchView.as_view(), name='celerity-search'),
    ),]

apphook_pool.register(SearchApphook)
