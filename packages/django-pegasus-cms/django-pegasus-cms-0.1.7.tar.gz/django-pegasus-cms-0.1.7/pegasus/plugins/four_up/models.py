#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.models import CMSPlugin, Page
from cms.models.fields import PlaceholderField
from django.db import models
from django.utils.translation import ugettext as _

from content.models import ArticleType, Issue, Topic

from model_utils import Choices


class FourUpPlugin(CMSPlugin):
    BACKFILL_CHOICES = Choices(('most_recent', _('Most Recent')),)
    title = models.CharField(max_length=255, null=False, blank=False)
    size = models.IntegerField(default=4) # TODO: validate multiple of 4
    backfill_method = models.CharField(max_length=20,
                                       choices=BACKFILL_CHOICES,
                                       null=False,
                                       default=BACKFILL_CHOICES.most_recent)
    backfill_article_type = models.ForeignKey(ArticleType,
                                              null=True,
                                              blank=True)
    backfill_issue = models.ForeignKey(Issue, null=True, blank=True)
    backfill_topic = models.ForeignKey(Topic, null=True, blank=True)

    def __unicode__(self):
        return self.title
