#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from django.template import Library
from search import order_explicitly
from search.models import CELERITY_SEARCHQUERYSET

register = Library()

@register.assignment_tag(takes_context=True)
def content_list(context,
                 article_types=[],
                 author=None,
                 count=10):

    request = context['request']

    sqs = CELERITY_SEARCHQUERYSET

    if article_types:
        sqs = sqs.filter(
            article_type__in=map(lambda t: t.slug or 'undefined',
                                 article_types))

    if author:
        sqs = sqs.filter(author_id=author.id)

    # explicitly order results
    sqs = order_explicitly(sqs, count)

    return sqs
