#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import re
import urllib
from urlparse import parse_qs, urlparse, urlunparse

from cms.models.pagemodel import Page
from django.template import Library
from django.template.defaultfilters import striptags, truncatewords_html
from django.utils.safestring import mark_safe

from content.models import Article, Issue, Topic

register = Library()


@register.filter
def multiply(value, factor):
    return value * factor

@register.filter
def order_by(qs, field_name_and_direction):
    return qs.order_by(field_name_and_direction)

@register.filter
def get_topic(nav_node):
    try:
        return Topic.objects.get(slug=nav_node.id)
    except Topic.DoesNotExist:
        return None

@register.filter
def prioritized_articles(nav_node, num_results=3):
    topic = get_topic(nav_node)
    if topic:
        return topic.articles[:num_results]
    return []

# from -> http://stackoverflow.com/a/12797728/163789
@register.filter
def times(number):
    return range(number)

@register.filter
def highlight(full_text, pattern):
    if pattern:
        return mark_safe(
            re.sub(r'({_pattern})'.format(_pattern=pattern),
                   r'<span class="highlight">\1</span>',
                   full_text))
    return full_text

@register.filter
def append_param(url, keyval):
    scheme, netloc, path, params, query, frag = urlparse(url)
    if query:
        return url + '&' + keyval
    return url + '?' + keyval

@register.simple_tag(takes_context=True)
def apply_param(context, param_name, val, allow_multiple=False, nullify=None):
    """ This function returns a URL that preserves all current GET params
        while applying a new param to filter by 'param_name' on 'val'."""

    request = context['request']

    if nullify:
        path = remove_param(context, nullify)
    else:
        path = request.get_full_path()

    url_parts = list(urlparse(path))
    params = parse_qs(url_parts[4], keep_blank_values=True) # index 4 is the query string
    active_filters = set(params.get(param_name, []))
    if not allow_multiple:
        active_filters.clear()
    active_filters.add(val)
    params[param_name] = list(active_filters)
    qs = urllib.urlencode(params, doseq=True)
    url_parts[4] = qs

    return urlunparse(url_parts)

@register.simple_tag(takes_context=True)
def remove_param(context, param_name, val=None):
    """ This function returns a URL which preserves all current GET params
        while removing the param to filter by 'param_name' on 'val', if the
        filter currently exists. If val==None, we will remove the parameter
        altogether."""

    request = context['request']

    url_parts = list(urlparse(request.get_full_path()))
    params = parse_qs(url_parts[4], keep_blank_values=True) # index 4 is the query string
    if val is not None:
        vals = params.get(param_name, [])
        for _param in vals:
            if _param == val:
                vals.remove(_param)
        params[param_name] = vals
    else:
        active_filters = params.get(param_name, [])
        if val in active_filters:
            active_filters.remove(val)
            params[param_name] = active_filters
    qs = urllib.urlencode(params, doseq=True)
    url_parts[4] = qs

    return urlunparse(url_parts)

@register.filter
def secure_url(url):
    return url.replace('http://', 'https://')
