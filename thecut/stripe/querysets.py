# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.db import models
import stripe


class CustomerQuerySet(models.query.QuerySet):

    def _get_api_key(self, account=None):
        if account is None:
            account_field = self.model._meta.get_field_by_name('account')[0]
            account = self._known_related_objects[account_field].values()[0]
        return account.secret_key

    def create(self, account=None, **kwargs):
        # Create a customer using the stripe API
        stripe_customer = stripe.Customer.create(
            api_key=self._get_api_key(account=account), **kwargs)
        # Create a customer model instance
        extra_kwargs = {'account': account} if account else {}
        return super(CustomerQuerySet, self).create(
            stripe_id=stripe_customer.id, **extra_kwargs)
