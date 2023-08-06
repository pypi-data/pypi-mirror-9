#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from django.template import Library

register = Library()



@register.assignment_tag(takes_context=True)
def get_filter_active_state(context,
                            filter_name=None,
                            val=None,
                            mutex=None,
                            contains=None):

    """ This function returns either 'active' or 'inactive', depending on the
        current URL's filter GET parameters."""

    request = context['request']
    classes = {True: 'active', False: 'inactive'}

    if filter_name:
        if mutex and mutex in request.GET:
            is_active = False
        else:
            if val is not None:
                active_filters = request.GET.getlist(filter_name)
                is_active = unicode(val) in active_filters
            else:
                is_active = filter_name in request.GET
    elif contains:
        is_active = all(k in request.GET for k in contains.split(','))

    return classes[is_active]
