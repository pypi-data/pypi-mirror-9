#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.models import CMSPlugin
from django.db import models
from django.utils.translation import ugettext as _

from content.models import Article


# TODO: should we rename TombstonePlugin to ArticlePlugin, or similar?


class TombstonePlugin(CMSPlugin):
    article = models.ForeignKey(Article, null=True, blank=True)
    promo_text = models.CharField(max_length=255,
                                  null=True,
                                  blank=True)
    highlighted_text = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=(('Phrases matching this text will be highlighted in '
                    'red when appearing in headlines.')))
    image = models.ImageField(_("image"),
                              upload_to=CMSPlugin.get_media_path,
                              null=True,
                              blank=True)
    image_alt_text = models.CharField(max_length=255, null=True, blank=True)
