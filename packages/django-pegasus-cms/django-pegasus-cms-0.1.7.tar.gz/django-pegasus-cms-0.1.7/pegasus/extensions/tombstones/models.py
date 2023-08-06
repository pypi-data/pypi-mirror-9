#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool
from content.models import Article
from django.db import models
from model_utils import Choices


class TombstonesExtension(PageExtension):
    class Meta:
        verbose_name = 'Tombstones'
        verbose_name_plural = verbose_name

    def copy_relations(self, old_instance, lang):
        self.highlight_set.all().delete()
        for highlight in old_instance.highlight_set.all():
            highlight.pk = None
            highlight.extension = self
            highlight.save()

class Highlight(models.Model):
    IMAGE_CHOICES = Choices(
        'policy',
        'litigation',
        'multimedia',
        'legislation',)
    extension = models.ForeignKey(TombstonesExtension, null=False, blank=False)
    headline = models.CharField(max_length=255, null=False, blank=False)
    image = models.CharField(max_length=30,
                             choices=IMAGE_CHOICES,
                             null=False,
                             blank=False)
    image_alt_text = models.CharField(max_length=255, null=True, blank=True)
    promo_text = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return u'Tombstone: %s' % self.headline

extension_pool.register(TombstonesExtension)
