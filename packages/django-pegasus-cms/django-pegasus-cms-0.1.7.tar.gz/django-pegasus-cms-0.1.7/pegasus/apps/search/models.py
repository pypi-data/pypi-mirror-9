# -*- coding: utf-8 -*-

from haystack.query import SearchQuerySet

_sqs = SearchQuerySet()

CELERITY_SEARCHQUERYSET = _sqs\
    .exclude(django_ct='cms.title')  # don't include cms pages

__all__ = ['CELERITY_SEARCHQUERYSET']
