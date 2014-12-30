# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.db import models


class KnownFieldMixin(object):

    def _get_known_field_value(self, field_name):
        field = self.model._meta.get_field_by_name(field_name)[0]
        return self._known_related_objects[field].values()[0]


class CustomerQuerySet(KnownFieldMixin, models.query.QuerySet):

    def _get_account(self):
        return self._get_known_field_value('account')

    def create(self, account=None, plan=None, **kwargs):
        account = account or self._get_account()
        if plan:
            kwargs.update({'plan': plan.stripe_id})
        # Create a customer using the stripe API
        stripe_customer = self.model._stripe.Customer.create(
            api_key=account.secret_key, **kwargs)
        # Create a customer model instance
        customer = super(CustomerQuerySet, self).create(
            stripe_id=stripe_customer.id, account=account)
        # If a plan was provided, then we'll also want to sync subscriptions
        if plan:
            customer.subscriptions.sync()
        return customer


class PlanQuerySet(KnownFieldMixin, models.query.QuerySet):

    def _get_account(self):
        return self._get_known_field_value('account')

    def create(self, account=None, **kwargs):
        account = account or self._get_account()
        # Create a plan using the stripe API
        stripe_plan = self.model._stripe.Plan.create(
            api_key=account.secret_key, **kwargs)
        # Create a plan model instance
        return super(PlanQuerySet, self).create(
            stripe_id=stripe_plan.id, account=account)


class SubscriptionQuerySet(KnownFieldMixin, models.query.QuerySet):

    def _get_customer(self):
        return self._get_known_field_value('customer')

    def _get_plan(self):
        return self._get_known_field_value('plan')

    def create(self, customer=None, plan=None, **kwargs):
        customer = customer or self._get_customer()
        plan = plan or self._get_plan()
        # Create a subscription using the stripe API
        stripe_subscription = customer.api().subscriptions.create(
            plan=plan.stripe_id, **kwargs)
        # Create a subscription model instance
        return super(SubscriptionQuerySet, self).create(
            stripe_id=stripe_subscription.id, account=customer.account,
            customer=customer, plan=plan)
