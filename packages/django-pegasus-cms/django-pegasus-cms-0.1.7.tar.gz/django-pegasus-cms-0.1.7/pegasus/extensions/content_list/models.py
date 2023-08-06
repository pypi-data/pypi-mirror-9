#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool
from content.models import Article, ArticleType
from django.core.urlresolvers import NoReverseMatch, reverse
from django.db import models
from model_utils import Choices


class ContentListExtension(PageExtension):
    class Meta:
        verbose_name = 'Content Lists'
        verbose_name_plural = verbose_name

    def copy_relations(self, old_instance, lang):
        """ When a page is published, Django-CMS creates a new copy of the
            page, so we need to make sure to manually copy over any many-to-
            many fields."""

        self.contentlist_set.all().delete()
        for content_list in old_instance.contentlist_set.all():
            article_types = content_list.list_article_type_filter.all()
            content_list.pk = None
            content_list.extension = self
            content_list.save()
            for article_type in article_types:
                content_list.list_article_type_filter.add(article_type)
            content_list.save()

    def __unicode__(self):
        try:
            # TODO: be inclusive of ALL the content lists here?
            return self.contentlist_set.all()[0].list_title
        except:
            return 'Empty Content List'


class ContentList(models.Model):
    list_title = models.CharField(max_length=255,
                                  null=False,
                                  default='Content List')
    list_article_type_filter = models.ManyToManyField(ArticleType,
                                                      null=True,
                                                      blank=True)
    extension = models.ForeignKey(ContentListExtension, null=True, blank=True)

    def __unicode__(self):
        return self.list_title

    def get_absolute_url(self):
        _url = ''
        try:
            _url = reverse('celerity-search')
            _filters = self.list_article_type_filter.all()
            if _url and _filters:
                _querystring = '&'.join(
                    ['article_type=%s' % atype.slug for atype in _filters])
                if _querystring:
                    _url = _url + '?' + _querystring
        except NoReverseMatch:
            pass
        return _url

    @property
    def article_type_filter(self):
        return self.list_article_type_filter

    @property
    def title(self):
        return self.list_title

    @property
    def url(self):
        return self.get_absolute_url()

extension_pool.register(ContentListExtension)
