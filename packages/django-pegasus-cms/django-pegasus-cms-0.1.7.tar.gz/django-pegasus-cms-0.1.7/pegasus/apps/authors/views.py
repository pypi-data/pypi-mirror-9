#!/usr/bin/env python
# -*- coding: utf-8 -*-

from content.models import ArticleType
from django.views.generic import DetailView, ListView

from .models import Author, Department


class AuthorDetail(DetailView):
    model = Author
    template_name = 'authors/expert-detail.html'
    context_object_name = 'author'

    def get_context_data(self, **kwargs):
        context_data = super(AuthorDetail, self).get_context_data(**kwargs)
        context_data['doc_article_types'] = ArticleType.get_work_article_types()
        context_data['doc_viewall_link'] = ''
        context_data['content_model'] = self.model
        context_data['media_article_types'] = ArticleType.get_media_article_types()
        return context_data

class AuthorList(ListView):
    model = Author
    template_name = 'pegasus/pages/team.html'
    context_object_name = 'authors'
