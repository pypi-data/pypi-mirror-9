#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.cms_toolbar import ADMIN_MENU_IDENTIFIER, ADMINISTRATION_BREAK
from cms.toolbar.items import Break, SubMenu
from cms.toolbar_base import CMSToolbar
from cms.toolbar_pool import toolbar_pool
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


@toolbar_pool.register
class ArticleToolbar(CMSToolbar):

    def populate(self):
        menu = self.toolbar.get_or_create_menu('article-menu', _('Articles'))

        url = reverse('admin:content_article_changelist')
        menu.add_sideframe_item(_('Article List'), url=url)

        url = reverse('admin:content_article_add')
        menu.add_modal_item(_('Add New Article'), url=url)


@toolbar_pool.register
class CaseToolbar(CMSToolbar):

    def populate(self):
        menu = self.toolbar.get_or_create_menu('case-menu', _('Cases'))

        url = reverse('admin:content_case_changelist')
        menu.add_sideframe_item(_('Case List'), url=url)

        url = reverse('admin:content_case_add')
        menu.add_modal_item(_('Add New Case'), url=url)


@toolbar_pool.register
class TopicToolbar(CMSToolbar):

    def populate(self):
        menu = self.toolbar.get_or_create_menu('topic-menu', _('Topics'))

        url = reverse('admin:content_topic_changelist')
        menu.add_sideframe_item(_('Topic List'), url=url)

        url = reverse('admin:content_topic_add')
        menu.add_modal_item(_('Add New Topic'), url=url)


@toolbar_pool.register
class IssueToolbar(CMSToolbar):

    def populate(self):
        menu = self.toolbar.get_or_create_menu('issue-menu', _('Issues'))

        url = reverse('admin:content_issue_changelist')
        menu.add_sideframe_item(_('Issue List'), url=url)

        url = reverse('admin:content_issue_add')
        menu.add_modal_item(_('Add New Issue'), url=url)


@toolbar_pool.register
class PromoToolbar(CMSToolbar):

    def populate(self):
        menu = self.toolbar.get_or_create_menu('promo-menu', _('Promos'))

        url = reverse('admin:content_promoplacement_changelist')
        menu.add_sideframe_item(_('Promo List'), url=url)

        url = reverse('admin:content_promoplacement_add')
        menu.add_modal_item(_('Add New Promo'), url=url)


@toolbar_pool.register
class EventToolbar(CMSToolbar):

    def populate(self):
        menu = self.toolbar.get_or_create_menu('event-menu', _('Events'))

        url = reverse('admin:content_event_changelist')
        menu.add_sideframe_item(_('Event List'), url=url)

        url = reverse('admin:content_event_add')
        menu.add_modal_item(_('Add New Event'), url=url)
