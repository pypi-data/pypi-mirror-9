#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import logging

from content.models import Issue, Topic

logger = logging.getLogger('django-pegasus-cms')


class CelerityFacetedSearchFallbackMixin(object):

    def _apply_mock_facets(self, sqs):
        # Whoosh backend does not support faceting, so let's fake it.
        self.facet_counts = {
            'fields': {
                'article_type': [],
                'content_type': [],
                'issue': [],
                'topic': [],
            },
        }

        try:
            article_types = filter(None, # remove empty elements
                                   set(sqs.values_list(
                                       'article_type', flat=True)))
            for article_type in article_types:
                # Don't bother counting elements... use hard-coded value
                self.facet_counts['fields']['article_type'].append(
                    (article_type, '?'))
            content_types = filter(None, # remove empty elements
                                   set(sqs.values_list(
                                       'content_type', flat=True)))
            for content_type in content_types:
                # Don't bother counting elements... use hard-coded value
                self.facet_counts['fields']['content_type'].append(
                    (content_type, '?'))
            issues = [i.name for i in Issue.objects.all()]
            topics = [t.name for t in Topic.objects.all()]
            for issue in issues:
                # Don't bother counting elements... use hard-coded value
                self.facet_counts['fields']['issue'].append((issue, '?'))
            for topic in topics:
                # Don't bother counting elements... use hard-coded value
                self.facet_counts['fields']['topic'].append((topic, '?'))
        except Exception as e:
            logger.warning(e)
