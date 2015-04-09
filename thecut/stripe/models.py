# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from . import managers, querysets, settings, utils
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
from thecut.stripe import errors

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

    def api(self, refresh=False, clear=False):
        key = 'thecut.stripe:{0}:{1}:api_data'.format(self._api_cache_name,
                                                      self.pk)
        if clear:
            return cache.delete(key)
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
            try:
                return self.api().get('display_name')
            except stripe.error.AuthenticationError:
                # This is to stop exception from Stripe breaking admin site.
                # See also Note in `stripe_id`
                return 'Authentication error'
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
                                                   key=self.secret_key)

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
            try:
                return self.api().get('id')
            except:
                return None

                # TODO: Note: this is probably a bad idea.
                # But as a temporary workaround it returns None as if 
                # 'secret_key' not set.

                # Reason for this is broken admin site (stripe_id is included in
                # list) if application access has been revoked / key has expired.

                # Stripe started to throw this kind of exception on opening of
                # ConnectedAccount list:

                # Exception Type: AuthenticationError at /admin/stripe/connectedaccount/
                # Exception Value: Expired API key provided: sk_test_********************KG8l.  Application access may have been revoked.

                #  Traceback (only relevant parts):
# File "lib/python2.7/site-packages/django/contrib/admin/templatetags/admin_list.py" in items_for_result
#   185.             f, attr, value = lookup_field(field_name, result, cl.model_admin)
# File "lib/python2.7/site-packages/django/contrib/admin/util.py" in lookup_field
#   258.                 value = attr()
# File "lib/python2.7/site-packages/thecut/stripe/models.py" in stripe_id
#   137.             return self.api().get('id')
# File "lib/python2.7/site-packages/thecut/stripe/models.py" in api
#   51.         resource = self._get_api_resource()
# File "lib/python2.7/site-packages/thecut/stripe/models.py" in _get_api_resource
#   107.         return self._stripe.Account.retrieve(api_key=self.secret_key)
# File "lib/python2.7/site-packages/stripe/resource.py" in retrieve
#   240.                                                          api_key=api_key)
# File "lib/python2.7/site-packages/stripe/resource.py" in retrieve
#   186.         instance.refresh()
# File "lib/python2.7/site-packages/stripe/resource.py" in refresh
#   190.         self.refresh_from(self.request('get', self.instance_url()))
# File "lib/python2.7/site-packages/stripe/resource.py" in request
#   131.         response, api_key = requestor.request(method, url, params)
# File "lib/python2.7/site-packages/stripe/api_requestor.py" in request
#   124.         resp = self.interpret_response(rbody, rcode)
# File "lib/python2.7/site-packages/stripe/api_requestor.py" in interpret_response
#   231.             self.handle_api_error(rbody, rcode, resp)
# File "lib/python2.7/site-packages/stripe/api_requestor.py" in handle_api_error
#   141.                 err.get('message'), rbody, rcode, resp)
#
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


@python_2_unicode_compatible
class Charge(StripeAPIMixin, models.Model):
    """Stripe Charge."""

    account = models.ForeignKey('stripe.Account', related_name='charges',
                                editable=False, on_delete=models.PROTECT)

    stripe_id = models.CharField('Stripe ID', max_length=255, db_index=True,
                                 editable=False)

    customer = models.ForeignKey('stripe.Customer',
                                 related_name='charges', editable=False,
                                 null=True, blank=True,
                                 on_delete=models.PROTECT)

    objects = managers.ChargeManager.for_queryset_class(
        querysets.ChargeQuerySet)()

    class Meta(object):
        unique_together = ['account', 'stripe_id']

    def __str__(self):
        return self.stripe_id

    def _construct_api_resource(self, cache_data):
        return self._stripe.Charge.construct_from(
            json.loads(cache_data), key=self.account.secret_key)

    def _get_api_resource(self):
        return self._stripe.Charge.retrieve(id=self.stripe_id,
                                            api_key=self.account.secret_key)

    @property
    def amount(self):
        return Decimal(self.api().get('amount', '0')) / 100


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
            json.loads(cache_data), key=self.account.secret_key)

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
            utils.parse_timestamp(invoice.date)

    def get_cards(self):
        """
        Fetches stripe api ``sources`` list and returns only ``card`` objects.
        :return: :py:class:``list`` of :py:class:``stripe.resource.Card``
        """
        api = self.api()
        if api.get('deleted'):
            return []
        return self.api().sources.all(object='card').data

    def get_card(self, card_id):
        """
        Retrieves stripe api ``source`` but returns it only of it is  a ``card``

        :return: :py:class:``stripe.resource.Card`` or raises
            :py:class:``.errors/SourceIsWrongType`` if type of returned object
            is not ``card``.
        """
        api = self.api()
        if api.get('deleted'):
            return None

        source = self.api().sources.retrieve(card_id)
        if source['object'] != 'card':
            raise errors.SourceIsOfWrongType(
                'Got {} instead of card, card_id={}'.format(
                    source['object'], card_id))

        return source


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
            json.loads(cache_data), key=self.account.secret_key)

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
            json.loads(cache_data), key=self.account.secret_key)

    def _get_api_resource(self):
        return self.customer.api().subscriptions.retrieve(id=self.stripe_id)

    @property
    def canceled_at(self):
        return utils.parse_timestamp(self.api().get('canceled_at'))

    @property
    def current_period_ends_at(self):
        return utils.parse_timestamp(self.api().get('current_period_end'))

    @property
    def current_period_starts_at(self):
        return utils.parse_timestamp(self.api().get('current_period_start'))

    @property
    def ended_at(self):
        return utils.parse_timestamp(self.api().get('ended_at'))

    @property
    def started_at(self):
        return utils.parse_timestamp(self.api().get('start'))
