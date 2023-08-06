#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import logging
from datetime import timedelta

from django.utils import timezone
from haystack.forms import FacetedModelSearchForm

from .utils import CelerityFacetedSearchFallbackMixin

logger = logging.getLogger('pegasus')


class CeleritySearchForm(FacetedModelSearchForm,
                         CelerityFacetedSearchFallbackMixin):

    def no_query_found(self):
        """ If an empty search query is passed, assume that all results are
            being requested."""
        return self.searchqueryset.all()

    def search(self):
        sqs = super(CeleritySearchForm, self).search()

        # get base facets
        self.facet_counts = sqs.facet('content_type')\
                               .facet('article_type')\
                               .facet('topic')\
                               .facet('issue')\
                               .facet_counts()

        # fake faceting, if necessary
        if not self.facet_counts:
            self._apply_mock_facets(sqs)  # from CelerityFacetedSearchFallbackMixin

        # apply filters from form
        for k, v in getattr(self.data, 'iterlists', lambda: {})():
            if k == 'topic':
                sqs = sqs.filter(topic__in=v)
            elif k == 'issue':
                sqs = sqs.filter(issue__in=v)
            elif k == 'article_type':
                sqs = sqs.filter(article_type__in=v)
            elif k == 'content_type':
                sqs = sqs.filter(content_type__in=v)
            elif k == 'min_age':
                sqs = sqs.filter(
                    pub_date__lte=timezone.now()-timedelta(days=int(v[0])))
            elif k == 'max_age':
                sqs = sqs.filter(
                    pub_date__gte=timezone.now()-timedelta(days=int(v[0])))

        return sqs
