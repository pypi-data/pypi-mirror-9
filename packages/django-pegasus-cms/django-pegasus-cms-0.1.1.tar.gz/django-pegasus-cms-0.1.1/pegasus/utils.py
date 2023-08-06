#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division

import hashlib
import logging

from django.core.cache import get_cache, InvalidCacheBackendError

logger = logging.getLogger('django-pegasus-cms')

try:
    cache = get_cache('decorated')
except InvalidCacheBackendError:
    cache = get_cache('default')


def get_func_cache_key(f, *args, **kwargs):

    serialize = [unicode(f.__name__)]

    for arg in args:
        try:
            serialize.append(unicode(arg))
        except UnicodeDecodeError as e1:
            try:
                serialize.append(str(arg))
            except UnicodeEncodeError as e2:
                return None
        except Exception as e3:
            #logger.warning('unable to form cache key for func: %s' % f.__name__)
            return None

    for k,v in kwargs.iteritems():
        serialize.append(unicode(k) + '=' + unicode(v))

    try:
        key = hashlib.sha1(unicode('/'.join(serialize)).encode('utf-8')).hexdigest()
    except:
        #logger.warning('unable to form cache_key for: (args[%s] kwargs[%s]' % (
        #    args, kwargs))
        return None

    return key


class cache_for(object):

    def __init__(self, seconds=0, minutes=None, hours=None):
        if hours and minutes and seconds:
            self.seconds = hours*60*60 + minutes*60 + seconds
        elif hours and minutes:
            self.seconds = hours*60*60 + minutes*60
        elif hours and seconds:
            self.seconds = hours*60*60 + seconds
        elif minutes and seconds:
            self.seconds = minutes*60 + seconds
        elif hours:
            self.seconds = hours*60*60
        elif minutes:
            self.seconds = minutes*60
        elif seconds:
            self.seconds = seconds

    def __call__(self, f):

        def wrapped_f(*args, **kwargs):
            cached_val = None

            cache_key = get_func_cache_key(f, *args, **kwargs)
            if cache_key:
                cached_val = cache.get(cache_key)

            if cached_val:
                return cached_val

            ret_val = f(*args, **kwargs)
            cache.set(cache_key, ret_val, self.seconds)
            return ret_val

        return wrapped_f
