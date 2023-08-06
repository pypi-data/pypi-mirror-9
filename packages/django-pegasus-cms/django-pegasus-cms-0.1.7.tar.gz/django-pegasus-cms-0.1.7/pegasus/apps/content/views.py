#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from django.utils import timezone
from django.views.generic import DetailView, ListView

from .models import Article, Case, Event, LegalTeam


class CelerityContentTypeDetailView(DetailView):
    template_name = 'partials/article.html'
    context_object_name = 'article'

    def get_queryset(self):
        qs = super(CelerityContentTypeDetailView, self).get_queryset()
        return qs.filter(date_published__lte=timezone.now())

    def get_context_data(self, **kwargs):
        context = super(CelerityContentTypeDetailView, self).get_context_data(**kwargs)
        context['content_model'] = self.model
        return context

class CelerityContentTypeListView(ListView):
    def get_queryset(self):
        page_id = self.kwargs['page_id']
        return self.model.objects.filter(page__id=page_id).filter(
            date_published__lte=timezone.now())


class ArticleDetail(CelerityContentTypeDetailView):
    model = Article
    context_object_name = 'article'


class ArticleList(CelerityContentTypeListView):
    model = Article


class CaseDetail(CelerityContentTypeDetailView):
    model = Case

    def get_context_data(self, **kwargs):
        context = super(CaseDetail, self).get_context_data(**kwargs)
        context['legal_team'] = LegalTeam.objects.filter(case=context['object'])
        return context


class EventDetail(CelerityContentTypeDetailView):
    model = Event
    template_name = 'pegasus/event-page.html'
    context_object_name = 'event'
