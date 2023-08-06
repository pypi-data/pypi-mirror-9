#!/usr/bin/env python
# -*- coding: utf-8 -*-

from authors.models import Author, Department
from content.models import Article
from django.template import Library

register = Library()

@register.assignment_tag
def get_all_departments():
    depts = Department.objects.all()
    return depts


@register.assignment_tag
def related_articles(author, max_numb=2, exclude=None):
    qs = Article.objects.filter(author=author)
    if exclude:
        qs = qs.exclude(id=exclude.id)
    return qs[:max_numb]

@register.inclusion_tag('partials/team-list.html')
def get_author_list():
    return {'authors': Author.objects.all()}
