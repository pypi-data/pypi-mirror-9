# -*- coding: utf-8 -*-
from haystack.exceptions import SearchBackendError
import logging

logger = logging.getLogger('search')

def order_explicitly(sqs, count=None, f=None):
    original_sqs = sqs
    try:
        if f:
            return f(sqs, count)
        sqs = sqs.order_by('-featured', 'priority', '-pub_date')
        if count:
            sqs = sqs[:count]
    except SearchBackendError as e:
        logger.warning(e)
        return original_sqs
    return sqs
