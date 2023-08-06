#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.template.defaultfilters import striptags, truncatewords_html
from django.utils.translation import ugettext as _

from .models import MastheadPlugin


class CMSMastheadPlugin(CMSPluginBase):
    model = MastheadPlugin
    module = _('Masthead')
    name = _('Masthead Plugin')
    allow_children = True
    child_classes = ['CMSTombstonePlugin']
    render_template = 'cms/plugins/masthead.html'

    def render(self, context, instance, placeholder):
        # update the context
        context.update({
            'instance': instance,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(CMSMastheadPlugin)
