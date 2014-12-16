# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.utils import timezone


def parse_timestamp(timestamp):
    if timestamp:
        # Stripe timestamps are in UTC
        return timezone.make_aware(timezone.datetime.fromtimestamp(timestamp),
                                   timezone.pytz.UTC)
