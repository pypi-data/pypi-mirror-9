#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

from .menu import ContentMenu


class ContentApphook(CMSApp):
    name = _('Content')
    urls = ['content.urls']
    app_name = 'content'
    menus = [ContentMenu, ]

apphook_pool.register(ContentApphook)
