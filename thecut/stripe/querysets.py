# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.db import models


class KnownFieldMixin(object):

    def _get_known_field_value(self, field_name):
        """
        If queryset was called on concrete model (like account.charges.all())
        this method can be used to get this concrete model.


        Note: It returns None if it can't find field (instead of raising
            KeyError).
        Example:
        if queryset is called like this:
            ``account123.charges.create(...)``
        inside ``.create`` method call to
            ``self._get_known_field_value('account')``
        will return ``account123``.

        But inside ``Charge.objects.create(..)`` it will return ``None``.

        Note 2: if the child model (``charge`` in the example) does not have
            ``field_name`` field this method will raise ``FieldDoesNotExist``.

        """
        field = self.model._meta.get_field_by_name(field_name)[0]
        try:
            return self._known_related_objects[field].values()[0]
        except KeyError:
            return None

    def _get_account(self):
        return self._get_known_field_value('account')


class ChargeQuerySet(KnownFieldMixin, models.query.QuerySet):

    def _get_customer(self):
        return self._get_known_field_value('customer')

    def create(self, customer=None, account=None, **kwargs):
        """
        Charges can be created in various different ways:

        1) Charge.objects.create(account=aa, amount=xx, card=yy)
            - no customer set, charge on a connected account
            - account has to be provided
        2) account.charges.create(amount=xx, card=yy)
        3) customer.charges.create(amount=xx[, card=yy])
            - Resulting charge will have customer set
            - account is optional

        This method does sanity checks for parameters and raises ``ValueError``
        if combination of customer and account parameters and call method does
        not make sense.

        :return: :py:class:`thecut.stripe.models.Charge`
        """

        # "parent" as in before .
        # If we are called on concrete model like this ``acc.charges.create()``
        # parent_account = acc
        parent_customer = self._get_customer()
        parent_account = self._get_account()

        if customer and parent_customer and customer != parent_customer:
            # If called ``customer_john.charges.create(customer=customer_dick)``
            raise ValueError("Conflicting customer instances provided")
        if account and parent_account and account != parent_account:
            # If called ``account_a.charges.create(account=account_b)``
            raise ValueError("Conflicting account instances provided")

        customer = customer or parent_customer
        account = account or parent_account
        if customer and account and customer.account != account:
            raise ValueError("Customer has conflicting account")

        if customer:
            # Create a charge using the stripe's customer api
            stripe_charge = customer.api().charges().create(
                customer=customer.stripe_id, **kwargs)
            # Create a charge model instance
            return super(ChargeQuerySet, self).create(
                stripe_id=stripe_charge.id, account=customer.account,
                customer=customer)
        elif account:
            # Create a charge using the stripe API
            stripe_charge = self.model._stripe.Charge.create(
                api_key=account.secret_key, **kwargs)
            # Create a customer model instance
            return super(ChargeQuerySet, self).create(
                stripe_id=stripe_charge.id, account=account)
        else:
            raise ValueError("Account or customer should be provided")


class CustomerQuerySet(KnownFieldMixin, models.query.QuerySet):

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
