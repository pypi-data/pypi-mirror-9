#!/usr/bin/env python
# encoding: utf-8
from django.conf import settings

COUNT_VALUE_AFTER_RESET = 1
DEFAULT_COUNT_VALUE     = 0

THROTTLING_CONFIG             = getattr(settings, 'THROTTLING_CONFIG', {})
THROTTLING_STATUS_CODE        = getattr(settings, 'THROTTLING_STATUS_CODE', 429)
THROTTLING_INTERVAL           = getattr(settings, 'THROTTLING_INTERVAL', 60*24)
THROTTLING_NUMBER_OF_REQUESTS = getattr(settings, 'THROTTLING_NUMBER_OF_REQUESTS', 1000)
