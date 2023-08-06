#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import math

from django.utils import timezone
from haystack import indexes
from sorl.thumbnail import get_thumbnail

from .models import Article, Case, Event


class CelerityContentTypeIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    article_type = indexes.CharField(model_attr='article_type__name',
                                     faceted=True)
    content_type = indexes.CharField(model_attr='_meta__verbose_name_plural',
                                     faceted=True)
    title = indexes.CharField(model_attr='headline')
    subheading = indexes.CharField()
    priority = indexes.IntegerField(model_attr='priority', indexed=False)
    featured = indexes.BooleanField(model_attr='featured', indexed=False)
    topic = indexes.CharField(faceted=True)
    topic_url = indexes.CharField(indexed=False)
    issue = indexes.CharField(faceted=True)
    issue_url = indexes.CharField(indexed=False)
    issues = indexes.CharField()
    image_url = indexes.CharField(indexed=False)
    image_106_url = indexes.CharField(indexed=False)
    image_200_url = indexes.CharField(indexed=False)
    image_alt_text = indexes.CharField()
    summary = indexes.CharField()
    url = indexes.CharField(indexed=False)
    pub_date = indexes.DateTimeField(model_attr='date_published')
    author = indexes.CharField()
    author_id = indexes.IntegerField(indexed=False)
    author_url = indexes.CharField(indexed=False)

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            date_published__lte=timezone.now()).select_related(
                'author', 'article_type',).prefetch_related(
                    'issues', 'issues__topic')

    def get_updated_field(self):
        return 'modified'

    def prepare(self, obj):
        data = super(CelerityContentTypeIndex, self).prepare(obj)

        boost = 1.0

        # boost by featured
        if data['featured']:
            boost += 1.0

        # apply 'priority' boost
        # priority 5 == boost - 0.2
        # priority 3 == boost * 1
        # priority 1 == boost + 0.2
        boost += (0.3 - (data['priority'] * 0.1))

        # boost by publish date
        seconds_old = max(1.0,
                          (timezone.now() - data['pub_date']).total_seconds())
        days_old = seconds_old / (60*60*24)
        boost += (30 / (6 + days_old**0.5))

        # record boost param
        data['boost'] = boost
        return data

    def prepare_issue(self, obj):
        if obj.issue:
            return obj.issue.name
        return u''

    def prepare_issue_url(self, obj):
        if obj.issue:
            return obj.issue.get_absolute_url()
        return u''

    def prepare_image_url(self, obj):
        if obj.image:
            return obj.image
        return u''

    def prepare_image_106_url(self, obj):
        try:
            return get_thumbnail(obj.image, '106').url
        except:
            return getattr(obj, 'image', u'')

    def prepare_image_200_url(self, obj):
        try:
            return get_thumbnail(obj.image, '200').url
        except:
            return getattr(obj, 'image', u'')

    def prepare_image_alt_text(self, obj):
        return getattr(obj, 'image_alt_text', u'Image | Pegasus CMS')

    def prepare_subheading(self, obj):
        if hasattr(obj, 'subheading'):
            return obj.subheading
        return u''

    def prepare_topic(self, obj):
        if obj.topic:
            return obj.topic.name
        return u''

    def prepare_topic_url(self, obj):
        if obj.topic:
            return obj.topic.url
        return u''

    def prepare_issues(self, obj):
        return u','.join([issue.name for issue in obj.issues.all()])

    def prepare_summary(self, obj):
        return obj.summary(100)

    def prepare_url(self, obj):
        return obj.get_absolute_url()

    def prepare_author_id(self, obj):
        if obj.author:
            return obj.author.id
        return -1

    def prepare_author(self, obj):
        if obj.author:
            return obj.author.full_name
        return u''

    def prepare_author_url(self, obj):
        if obj.author:
            return obj.author.get_absolute_url()
        return u''


class ArticleIndex(CelerityContentTypeIndex, indexes.Indexable):
    def get_model(self):
        return Article

class CaseIndex(CelerityContentTypeIndex, indexes.Indexable):
    def get_model(self):
        return Case

class EventIndex(CelerityContentTypeIndex, indexes.Indexable):
    def get_model(self):
        return Event
