#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool
from django.db import models


class LeftNavExtension(PageExtension):
    enabled = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Left Navigation'
        verbose_name_plural = 'Left Navigation'

extension_pool.register(LeftNavExtension)
