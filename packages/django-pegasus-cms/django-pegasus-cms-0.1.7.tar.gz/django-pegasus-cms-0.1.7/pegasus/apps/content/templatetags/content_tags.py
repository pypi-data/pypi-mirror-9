#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from content.models import Promo, PromoPlacement
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.template import Library

register = Library()

@register.filter
def summarize(article, num_words=15):
    """ Gets a text summary of the article. This is often used as the
        default 'promo text' for an article."""
    try:
        return article.summary(num_words)
    except:
        return article


@register.inclusion_tag('partials/promos.html')
def get_page_promos(page, position=None):
    # promos always use the public page
    page = page.get_public_object()
    promos = Promo.objects.fitler(page=page)
    if position is not None:
        promos = promos.filter(position=position)
    return {'promos': promos}


@register.inclusion_tag('partials/in-the-news.html')
def get_home_right_promos():
    return {'promos': Promo.objects.filter(page=1)}


@register.inclusion_tag('partials/upcoming_event.html')
def get_home_middle_promos():
    return {'promos': Promo.objects.filter(page=1)[:2]}

@register.assignment_tag(takes_context=True)
def get_promos(context, position=None):
    request = context.get('request', {})
    page = getattr(request, 'current_page', None)
    ContentModel = context.get('content_model', None)

    if ContentModel:  # Is it an Article/Case/Event?
        content_type = ContentType.objects.get_for_model(ContentModel)
        if content_type.model == 'author':
            object_id = context['author'].pk
        else:
            object_id = context['article'].pk

    elif page:  # Or is it a Page?
        page = page.get_public_object()  # Get published version of page
        content_type = ContentType.objects.get_for_model(page.__class__)
        object_id = page.pk

    else:  # Or is it something else entirely?
        # TODO: unsupported page type
        pass

    promos = PromoPlacement.objects.filter(
        content_type=content_type,
        object_id=object_id)

    if position:
        promos = promos.filter(position=position)

    return promos
