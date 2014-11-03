# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from model_utils.managers import PassThroughManager
import stripe


class ConnectedAccountManager(PassThroughManager):

    def get_queryset(self, *args, **kwargs):
        queryset = super(ConnectedAccountManager, self).get_queryset(*args,
                                                                     **kwargs)
        return queryset.filter(application__isnull=False)


class CustomerManager(PassThroughManager):

    def sync(self):  # Only works from account
        response = stripe.Customer.all(api_key=self.instance.secret_key,
                                       include=['total_count'])['data']
        for data in response:
            self.get_or_create(stripe_id=data['id'],
                               defaults={'_api_data': data})


class PlanManager(PassThroughManager):

    def sync(self):  # Only works from account
        response = stripe.Plan.all(api_key=self.instance.secret_key,
                                   include=['total_count'])['data']
        for data in response:
            self.get_or_create(stripe_id=data['id'],
                               defaults={'_api_data': data})


class StandardAccountManager(PassThroughManager):

    def get_queryset(self, *args, **kwargs):
        queryset = super(StandardAccountManager, self).get_queryset(*args,
                                                                    **kwargs)
        return queryset.filter(application__isnull=True)


class SubscriptionManager(PassThroughManager):

    def sync(self):  # Only works from customer
        response = stripe.Customer.retrieve(
            id=self.instance.stripe_id,
            api_key=self.instance.account.secret_key).subscriptions.all(
            include=['total_count'])['data']
        for data in response:
            plan = self.instance.account.plans.get(
                stripe_id=data['plan']['id'])
            self.get_or_create(stripe_id=data['id'],
                               account=self.instance.account, plan=plan,
                               defaults={'_api_data': data})
