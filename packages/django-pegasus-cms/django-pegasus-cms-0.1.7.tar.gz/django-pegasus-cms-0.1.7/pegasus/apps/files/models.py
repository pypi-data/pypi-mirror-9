#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import os

from django.db import models


class File(models.Model):
    file = models.FileField(upload_to='uploads', null=False, blank=False)

    def __unicode__(self):
        return self.name

    @property
    def name(self):
        return os.path.basename(self.file.name)

    @property
    def url(self):
        return self.file.url
