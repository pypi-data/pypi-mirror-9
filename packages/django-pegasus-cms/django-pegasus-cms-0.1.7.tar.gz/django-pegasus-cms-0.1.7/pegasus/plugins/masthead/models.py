#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import re

from cms.models import CMSPlugin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _
from model_utils import Choices


def validate_hex(value):
    if value:
        if not re.match('^\#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$', value):
            raise ValidationError(
                u'Invalid color. Must be a valid hex color e.g. #000000'
            )


class MastheadPlugin(CMSPlugin):
    image = models.ImageField(_('image'),
                              upload_to=CMSPlugin.get_media_path,
                              null=True,
                              blank=True)
    image_mask = models.CharField(max_length=7,
                                  null=True,
                                  blank=True,
                                  help_text='Hex code for an image mask',
                                  validators=[validate_hex])
    columns = models.SmallIntegerField(choices=Choices(1, 2), default=2)

    def hex_to_rgb(self):
        mask = self.image_mask.lstrip('#')
        lv = len(mask)
        return tuple(int(mask[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

    @property
    def red_mask(self):
        if self.image_mask:
            return self.hex_to_rgb()[0]
        return 76

    @property
    def green_mask(self):
        if self.image_mask:
            return self.hex_to_rgb()[1]
        return 92

    @property
    def blue_mask(self):
        if self.image_mask:
            return self.hex_to_rgb()[2]
        return 107
