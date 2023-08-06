#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from django.core.urlresolvers import NoReverseMatch, reverse
from django.http import HttpResponseRedirect
from search.views import CeleritySearchView


def error404(request):
    return CeleritySearchView.as_view()(request, is_404=True)

def redirect404(request):
    try:
        return HttpResponseRedirect(reverse('404'))
    except NoReverseMatch as e:
        return HttpResponseRedirect(reverse('pages-root'))
