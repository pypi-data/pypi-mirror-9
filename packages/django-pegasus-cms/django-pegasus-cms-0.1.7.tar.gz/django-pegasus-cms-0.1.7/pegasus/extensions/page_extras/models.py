#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool
from django.db import models


class PageExtrasExtension(PageExtension):
    description = models.TextField(null=True,
                                   blank=True,
                                   help_text=('Optional text to display at top '
                                              'of landing pages.'))

    class Meta:
        verbose_name = 'Page Extras'
        verbose_name_plural = verbose_name

extension_pool.register(PageExtrasExtension)
