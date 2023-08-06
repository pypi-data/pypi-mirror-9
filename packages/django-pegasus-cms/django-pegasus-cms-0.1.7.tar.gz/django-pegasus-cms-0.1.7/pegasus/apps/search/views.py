#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

#from aldryn_search.views import AldrynSearchView
from search.forms import CeleritySearchForm

from .models import CELERITY_SEARCHQUERYSET


from django.views.generic import View
class CeleritySearchView(View):
#class CeleritySearchView(AldrynSearchView):
    form_class = CeleritySearchForm
    template_name = 'search/search.html'

    def build_form(self, form_kwargs=None):
        form_kwargs['load_all'] = False
        form_kwargs['searchqueryset'] = CELERITY_SEARCHQUERYSET
        super(CeleritySearchView, self).build_form(form_kwargs)

    def get_queryset(self):
        sqs = super(CeleritySearchView, self).get_queryset()
        self.results = sqs # cache results in View for later use
        return sqs

    def get_context_data(self, **kwargs):
        context_data = super(CeleritySearchView, self).get_context_data(**kwargs)
        context_data['use_small_logo'] = True
        context_data['facets'] = self.form.facet_counts
        context_data['is_search_page'] = True
        context_data['is_404'] = self.kwargs.get('is_404', False)
        return context_data
