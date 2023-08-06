#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.api import get_page_draft
from cms.toolbar_base import CMSToolbar
from cms.utils import get_cms_setting
from cms.utils.permissions import has_page_change_permission
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import NoReverseMatch, reverse
from django.utils.translation import ugettext_lazy as _


class CelerityExtensionToolbar(CMSToolbar):
    """ Abstract base class for front-end editable toolbars on the site."""

    @property
    def extension_model(self):
        raise NotImplementedError(('Your toolbar instance must define an '
                                   'extension_model'))

    def populate(self):
        self.page = get_page_draft(self.request.current_page)

        if not self.page:
            return

        has_global_current_page_change_permission = False
        if get_cms_setting('PERMISSION'):
            has_global_current_page_change_permission = has_page_change_permission(self.request)

            can_change = (self.request.current_page and
                          self.request.current_page.has_change_permission(self.request))

            if has_global_current_page_change_permission or can_change:
                try:
                    extension_instance = self.extension_model.objects.get(
                        extended_object_id=self.page.id)
                except ObjectDoesNotExist:
                    extension_instance = None
                try:
                    if extension_instance:
                        url = reverse('admin:{app_label}_{model_name}_change'.format(
                                          app_label=self.extension_model._meta.app_label,
                                          model_name=self.extension_model._meta.model_name),
                                      args=(extension_instance.pk,))
                    else:
                        url = (reverse('admin:{app_label}_{model_name}_add'.format(
                                           app_label=self.extension_model._meta.app_label,
                                           model_name=self.extension_model._meta.model_name)) +\
                                       '?extended_object=%s' % self.page.pk)
                except NoReverseMatch:
                    pass
                not_edit_mode = not self.toolbar.edit_mode
                current_page_menu = self.toolbar.get_or_create_menu('page')
                current_page_menu.add_modal_item(
                    _(self.extension_model._meta.verbose_name),
                    url=url,
                    disabled=not_edit_mode)
