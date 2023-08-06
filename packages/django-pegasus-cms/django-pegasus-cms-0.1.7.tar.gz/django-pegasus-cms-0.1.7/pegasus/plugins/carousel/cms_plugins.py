#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _

from .models import CarouselPlugin


class CMSCarouselPlugin(CMSPluginBase):
    module = _('Carousel')
    name = _('Carousel Plugin')
    allow_children = True
    child_classes = ['CMSTombstonePlugin']
    render_template = 'cms/plugins/carousel.html'

    def render(self, context, instance, placeholder):
        context.update({
            'instance': instance,
            'placeholder': placeholder,
        })
        return context

plugin_pool.register_plugin(CMSCarouselPlugin)
