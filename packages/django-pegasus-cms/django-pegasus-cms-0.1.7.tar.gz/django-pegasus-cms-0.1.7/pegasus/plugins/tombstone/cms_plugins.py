#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _

from .models import TombstonePlugin


class CMSTombstonePlugin(CMSPluginBase):
    model = TombstonePlugin
    module = _('Tombstone')
    name = _('Tombstone')
    render_template = 'cms/plugins/tombstone.html'

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context

plugin_pool.register_plugin(CMSTombstonePlugin)
