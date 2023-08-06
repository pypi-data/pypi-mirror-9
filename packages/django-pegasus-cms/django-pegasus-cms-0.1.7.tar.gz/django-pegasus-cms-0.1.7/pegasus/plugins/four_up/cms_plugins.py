#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _

from content.models import Article, Issue, Topic
from content.templatetags.content_tags import summarize

from search import order_explicitly
from search.models import CELERITY_SEARCHQUERYSET

from .models import FourUpPlugin


class CMSFourUpPlugin(CMSPluginBase):
    model = FourUpPlugin
    module = _('4-Up')
    name = _('4-Up Plugin')
    allow_children = True
    child_classes = ['CMSTombstonePlugin']
    render_template = 'cms/plugins/four_up.html'

    def render(self, context, instance, placeholder):
        # do we require backfilling?
        slots_remaining = instance.size - len(
            instance.child_plugin_instances or [])
        backfill_pages = list()
        if slots_remaining > 0 and (instance.backfill_topic or
                                    instance.backfill_issue or
                                    instance.backfill_article_type):

            # if so, use search to obtain backfill content
            backfill_pages = CELERITY_SEARCHQUERYSET

            # check for category/tree to backfill
            if instance.backfill_article_type:
                backfill_pages = backfill_pages.filter(
                    article_type=instance.backfill_article_type.name)
            elif instance.backfill_topic:
                backfill_pages = backfill_pages.filter(
                    topic=instance.backfill_topic.name)
            elif instance.backfill_issue:
                backfill_pages = backfill_pages.filter(
                    issues__contains=instance.backfill_issue.name)

            # explicitly order results
            backfill_pages = order_explicitly(backfill_pages,
                                              slots_remaining)


        backfilled = list()
        for backfill_page in backfill_pages:
            backfilled.append({
                'article': backfill_page,
                'image': backfill_page.image_url,
                'promo_text': backfill_page.summary,
                'parent': {
                    'plugin_type': 'CMSFourUpPlugin',
                },
            })

        # update the context
        context.update({
            'instance': instance,
            'placeholder': placeholder,
            'backfill_pages': backfilled,
        })
        return context

plugin_pool.register_plugin(CMSFourUpPlugin)
