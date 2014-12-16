# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from . import managers, querysets, settings
from datetime import datetime
from decimal import Decimal
from django.core.cache import cache
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.django_orm import CredentialsField, Storage
import json
import stripe


# South introspection rules for oauth2client's CredentialsField
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules(
        [], ['^oauth2client\.django_orm\.CredentialsField'])


class StripeAPIMixin(models.Model):

    _stripe = stripe

    class Meta(object):
        abstract = True

    def _construct_api_resource(self, cache_data):
        raise NotImplementedError('This method should be overridden.')

    @cached_property
    def _api_cache_name(self):
        return self.__class__.__name__

    def _get_api_resource(self):
        raise NotImplementedError('This method should be overridden.')

    def api(self, refresh=False):
        key = 'thecut.stripe:{0}:{1}:api_data'.format(self._api_cache_name,
                                                      self.pk)
        if not refresh:
            cache_data = cache.get(key)
            if cache_data:
                return self._construct_api_resource(cache_data)
        resource = self._get_api_resource()
        cache.set(key, json.dumps(resource))
        return resource


class AccountOAuth2Credentials(models.Model):
    """Stores OAuth2 credentials for an Account."""

    # Very yucky to use the id like this, but it is required by oauth2client's
    # django_orm Storage, which blindly created new instances without checking
    # to see if one already exists - with an id, it gets saved over the top).
    id = models.OneToOneField('stripe.Account',
                              related_name='_oauth2_credentials',
                              primary_key=True)

    credentials = CredentialsField()


@python_2_unicode_compatible
class Account(StripeAPIMixin, models.Model):
    """Stripe Account."""

    application = models.ForeignKey('stripe.Application', null=True,
                                    related_name='accounts',
                                    on_delete=models.PROTECT)

    _secret_key = models.TextField('secret key', blank=True, default='')

    _publishable_key = models.TextField('publishable key', blank=True,
                                        default='')

    def __str__(self):
        if self.secret_key:
            return self.api().get('display_name')
        else:
            return 'Disconnected'

    @cached_property
    def _api_cache_name(self):
        return 'Account'  # This is so proxy models share the same cache name.

    def _get_connect_credentials(self, code):
        flow = self.application._get_connect_flow()
        return flow.step2_exchange(code)

    def _get_oauth2_storage(self):
        return Storage(AccountOAuth2Credentials, 'id', self, 'credentials')

    def _construct_api_resource(self, cache_data):
        return self._stripe.Account.construct_from(json.loads(cache_data),
                                                   api_key=self.secret_key)

    def _get_api_resource(self):
        return self._stripe.Account.retrieve(api_key=self.secret_key)

    @property
    def oauth2_credentials(self):
        storage = self._get_oauth2_storage()
        return storage.get()

    @oauth2_credentials.setter
    def oauth2_credentials(self, credentials):
        storage = self._get_oauth2_storage()
        return storage.put(credentials)

    @property
    def publishable_key(self):
        token_data = (self.oauth2_credentials
                      and self.oauth2_credentials.token_response)
        return self._publishable_key or (
            token_data and token_data.get('stripe_publishable_key'))

    @property
    def secret_key(self):
        return self._secret_key or (
            self.oauth2_credentials and self.oauth2_credentials.access_token)

    def store_credentials(self, code):
        self.oauth2_credentials = self._get_connect_credentials(code)
    store_credentials.alters_data = True

    def stripe_id(self):
        if self.secret_key:
            return self.api().get('id')
    stripe_id.short_description = 'Stripe ID'


@python_2_unicode_compatible
class Application(StripeAPIMixin, models.Model):
    """Stripe Connect Application."""

    account = models.ForeignKey('stripe.StandardAccount',
                                related_name='applications',
                                on_delete=models.PROTECT)

    client_id = models.TextField('Client ID')

    def __str__(self):
        return '{0}'.format(self.account)

    def _get_connect_flow(self, redirect_uri=None):
        return OAuth2WebServerFlow(
            client_id=self.client_id,
            client_secret=self.account.secret_key,
            scope=['read_write'],
            auth_uri=settings.CONNECT_AUTHORIZE_URL,
            token_uri=settings.CONNECT_ACCESS_TOKEN_URL,
            redirect_uri=redirect_uri,
            revoke_uri=None,
            user_agent=settings.USER_AGENT)

    def get_connect_authorize_url(self, redirect_uri):
        flow = self._get_connect_flow(redirect_uri)
        return flow.step1_get_authorize_url()


class ConnectedAccount(Account):

    objects = managers.ConnectedAccountManager.for_queryset_class(
        models.query.QuerySet)()

    class Meta(Account.Meta):
        proxy = True


@python_2_unicode_compatible
class Customer(StripeAPIMixin, models.Model):
    """Stripe Customer."""

    account = models.ForeignKey('stripe.Account', related_name='customers',
                                editable=False, on_delete=models.PROTECT)

    stripe_id = models.CharField('Stripe ID', max_length=255, db_index=True,
                                 editable=False)

    objects = managers.CustomerManager.for_queryset_class(
        querysets.CustomerQuerySet)()

    class Meta(object):
        unique_together = ['account', 'stripe_id']

    def __str__(self):
        return self.api().get('email') or self.stripe_id

    def _construct_api_resource(self, cache_data):
        return self._stripe.Customer.construct_from(
            json.loads(cache_data), api_key=self.account.secret_key)

    def _get_api_resource(self):
        return self._stripe.Customer.retrieve(id=self.stripe_id,
                                              api_key=self.account.secret_key)

    # TODO: Temporary
    def get_upcoming_invoice(self):
        try:
            invoice = self._stripe.Invoice.upcoming(
                customer=self.stripe_id, api_key=self.account.secret_key)
        except stripe.error.InvalidRequestError:
            pass
        else:
            return invoice

    # TODO: Temporary
    def get_upcoming_invoice_date(self):
        invoice = self.get_upcoming_invoice()
        if invoice:
            return datetime.fromtimestamp(invoice.date)


@python_2_unicode_compatible
class Plan(StripeAPIMixin, models.Model):
    """Stripe Payment Plan."""

    account = models.ForeignKey('stripe.Account', related_name='plans',
                                editable=False, on_delete=models.PROTECT)

    stripe_id = models.CharField('Stripe ID', max_length=255, db_index=True,
                                 editable=False)

    objects = managers.PlanManager.for_queryset_class(querysets.PlanQuerySet)()

    class Meta(object):
        unique_together = ['account', 'stripe_id']

    def __str__(self):
        return self.api().get('name') or self.stripe_id

    def _construct_api_resource(self, cache_data):
        return self._stripe.Plan.construct_from(
            json.loads(cache_data), api_key=self.account.secret_key)

    def _get_api_resource(self):
        return self._stripe.Plan.retrieve(id=self.stripe_id,
                                          api_key=self.account.secret_key)

    @property
    def amount(self):
        return Decimal(self.api().get('amount', '0')) / 100


class StandardAccount(Account):

    objects = managers.StandardAccountManager.for_queryset_class(
        models.query.QuerySet)()

    class Meta(Account.Meta):
        proxy = True


@python_2_unicode_compatible
class Subscription(StripeAPIMixin, models.Model):
    """Stripe Customer Subscription."""

    account = models.ForeignKey('stripe.Account', related_name='subscriptions',
                                editable=False, on_delete=models.PROTECT)

    stripe_id = models.CharField('Stripe ID', max_length=255, db_index=True,
                                 editable=False)

    customer = models.ForeignKey('stripe.Customer',
                                 related_name='subscriptions', editable=False,
                                 on_delete=models.PROTECT)

    plan = models.ForeignKey('stripe.Plan', related_name='subscriptions',
                             editable=False, on_delete=models.PROTECT)

    objects = managers.SubscriptionManager.for_queryset_class(
        querysets.SubscriptionQuerySet)()

    class Meta(object):
        unique_together = ['account', 'stripe_id']

    def __str__(self):
        return self.plan.api().get('name') or self.stripe_id

    def _construct_api_resource(self, cache_data):
        return self._stripe.Subscription.construct_from(
            json.loads(cache_data), api_key=self.account.secret_key)

    def _get_api_resource(self):
        return self.customer.api().subscriptions.retrieve(id=self.stripe_id)

    @staticmethod
    def _from_timestamp(timestamp):
        if timestamp:
            return datetime.fromtimestamp(timestamp)

    @property
    def canceled_at(self):
        return self._from_timestamp(self.api().get('canceled_at'))

    @property
    def current_period_ends_at(self):
        return self._from_timestamp(self.api().get('current_period_end'))

    @property
    def current_period_starts_at(self):
        return self._from_timestamp(self.api().get('current_period_start'))

    @property
    def ended_at(self):
        return self._from_timestamp(self.api().get('ended_at'))

    @property
    def started_at(self):
        return self._from_timestamp(self.api().get('start'))
