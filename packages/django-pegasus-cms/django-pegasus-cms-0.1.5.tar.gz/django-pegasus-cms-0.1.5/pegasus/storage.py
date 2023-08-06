#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

from boto.s3.connection import OrdinaryCallingFormat
from precompressed.storage.s3boto import CachedPrecompressedS3BotoStorage
from storages.backends.s3boto import S3BotoStorage
from storages.utils import setting


class CelerityStaticFilesStorage(CachedPrecompressedS3BotoStorage):
    def __init__(self, acl=None, bucket=None, **settings):
        settings['headers'] = {
            'Cache-Control': 'max-age=%s' % str(60*60*24*365)  # cache for 1 year
        }
        # django-precompressed does not handle querystring auth
        settings['querystring_auth'] = False
        super(CelerityStaticFilesStorage, self).__init__(
            acl,
            bucket or setting('CELERITY_STATICFILES_BUCKET'),
            **settings)

    def url(self, name, force=False):
        # Applies fix shown here:
        # http://code.larlet.fr/django-storages/issue/121/s3boto-admin-prefix-issue-with-django-14#comment-1604389
        _url = super(CelerityStaticFilesStorage, self).url(name, force)
        if name.endswith('/') and not _url.endswith('/'):
            _url += '/'
        return _url

class CelerityMediaFilesStorage(S3BotoStorage):
    def __init__(self, acl=None, bucket=None, **settings):
        settings['headers'] = {
            'Cache-Control': 'max-age=%s' % str(60*60)  # cache for 1 hour
        }
        # we can use querystring auth here, but i don't like it
        settings['querystring_auth'] = False
        super(CelerityMediaFilesStorage, self).__init__(
            acl,
            bucket or setting('CELERITY_MEDIAFILES_BUCKET'),
            **settings)
