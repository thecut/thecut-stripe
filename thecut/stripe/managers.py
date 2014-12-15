# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from model_utils.managers import PassThroughManager


class ConnectedAccountManager(PassThroughManager):

    def get_queryset(self, *args, **kwargs):
        queryset = super(ConnectedAccountManager, self).get_queryset(*args,
                                                                     **kwargs)
        return queryset.filter(application__isnull=False)


class CustomerManager(PassThroughManager):

    def sync(self, account=None):
        # TODO: Pagination
        account = self._get_account()
        response = self.model._stripe.Customer.all(
            api_key=account.secret_key, include=['total_count'])
        for item in response['data']:
            self.get_or_create(stripe_id=item['id'], account=account)


class PlanManager(PassThroughManager):

    def sync(self, account=None):
        # TODO: Pagination
        account = self._get_account()
        response = self.model._stripe.Plan.all(
            api_key=account.secret_key, include=['total_count'])
        for item in response['data']:
            self.get_or_create(stripe_id=item['id'], account=account)


class StandardAccountManager(PassThroughManager):

    def get_queryset(self, *args, **kwargs):
        queryset = super(StandardAccountManager, self).get_queryset(*args,
                                                                    **kwargs)
        return queryset.filter(application__isnull=True)


class SubscriptionManager(PassThroughManager):

    def sync(self, customer=None):
        customer = customer or self._get_customer()
        # TODO: Pagination
        response = self.model._stripe.Customer.retrieve(
            api_key=customer.account.secret_key,
            id=customer.stripe_id).subscriptions.all(include=['total_count'])
        for item in response['data']:
            plan, created = customer.account.plans.get_or_create(
                stripe_id=item['plan']['id'])
            self.get_or_create(stripe_id=item['id'],
                               account=customer.account, customer=customer,
                               plan=plan)
