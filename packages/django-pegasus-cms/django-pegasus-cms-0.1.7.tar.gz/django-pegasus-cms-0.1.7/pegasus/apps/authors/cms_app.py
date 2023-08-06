#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class AuthorApphook(CMSApp):
    name = _('Author')
    url = ['author.urls']
    app_name = 'authors'

apphook_pool.register(AuthorApphook)
