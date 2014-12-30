# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.conf import settings


CONNECT_ACCESS_TOKEN_URL = getattr(settings, 'STRIPE_CONNECT_ACCESS_TOKEN_URL',
                                   'https://connect.stripe.com/oauth/token')

CONNECT_AUTHORIZE_URL = getattr(settings, 'STRIPE_CONNECT_AUTHORIZE_URL',
                                'https://connect.stripe.com/oauth/authorize')

USER_AGENT = getattr(settings, 'STRIPE_USER_AGENT',
                     'thecut.stripe/0.1-dev '
                     '(The Cut; +http://www.thecut.net.au/)')
