# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from . import managers, settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from jsonfield import JSONField
from model_utils.fields import MonitorField
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.django_orm import CredentialsField, Storage
import stripe


# South introspection rules for oauth2client's CredentialsField
try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    add_introspection_rules(
        [], ['^oauth2client\.django_orm\.CredentialsField'])


class APIDataMixin(models.Model):
    """Cache/store API responses."""

    _api_data = JSONField('API data', null=True, blank=False, editable=False)

    _api_data_updated_at = MonitorField('API data updated at', null=True,
                                        blank=False, monitor='_api_data',
                                        editable=False)

    def api_data(self, refresh=False):
        if refresh or not self._api_data:
            self._api_data = self._get_api_data()
            self.save(update_fields=['_api_data'])
        return self._api_data

    class Meta(object):
        abstract = True


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
class Account(APIDataMixin, models.Model):
    """Stripe Account."""

    application = models.ForeignKey('stripe.Application', null=True,
                                    related_name='accounts', editable=False,
                                    on_delete=models.PROTECT)

    _secret_key = models.TextField('secret key', blank=True, default='')

    publishable_key = models.TextField(blank=True, default='')

    def __str__(self):
        return self.api_data().get('business_name')

    def _get_api_data(self):
        return stripe.Account.retrieve(api_key=self.secret_key)

    def _get_connect_credentials(self, code):
        flow = self.application._get_connect_flow()
        return flow.step2_exchange(code)

    def _get_oauth2_storage(self):
        return Storage(AccountOAuth2Credentials, 'id', self, 'credentials')

    @property
    def oauth2_credentials(self):
        storage = self._get_oauth2_storage()
        return storage.get()

    @oauth2_credentials.setter
    def oauth2_credentials(self, credentials):
        storage = self._get_oauth2_storage()
        return storage.put(credentials)

    @property
    def secret_key(self):
        return self._secret_key or self.oauth2_credentials.access_token

    def store_credentials(self, code):
        self.oauth2_credentials = self._get_connect_credentials(code)
    store_credentials.alters_data = True

    def stripe_id(self):
        return self.api_data().get('id')
    stripe_id.short_description = 'Stripe ID'


@python_2_unicode_compatible
class Application(models.Model):
    """Stripe Connect Application."""

    account = models.ForeignKey('stripe.Account', related_name='applications',
                                on_delete=models.PROTECT)

    client_id = models.TextField('Client ID')

    def __str__(self):
        return '{0}'.format(self.client_id)

    def _get_connect_flow(self):
        return OAuth2WebServerFlow(
            client_id=self.client_id,
            client_secret=self.account.secret_key,
            scope=['read_write'],
            auth_uri=settings.CONNECT_AUTHORIZE_URL,
            token_uri=settings.CONNECT_ACCESS_TOKEN_URL,
            redirect_uri='http://127.0.0.1:8000/',  # TODO
            revoke_uri=None,
            user_agent=settings.USER_AGENT)

    def get_connect_authorize_url(self):
        flow = self._get_connect_flow()
        return flow.step1_get_authorize_url()


@python_2_unicode_compatible
class Customer(APIDataMixin, models.Model):
    """Stripe Customer."""

    account = models.ForeignKey('stripe.Account', related_name='customers',
                                editable=False, on_delete=models.PROTECT)

    stripe_id = models.CharField('Stripe ID', max_length=255, db_index=True,
                                 editable=False)

    objects = managers.CustomerManager.for_queryset_class(
        models.query.QuerySet)()

    class Meta(object):
        unique_together = ['account', 'stripe_id']

    def __str__(self):
        return self.api_data().get('email')

    def _get_api_data(self):
        return stripe.Customer.retrieve(id=self.stripe_id,
                                        api_key=self.account.secret_key)


@python_2_unicode_compatible
class Plan(APIDataMixin, models.Model):
    """Stripe Subscription Plan."""

    account = models.ForeignKey('stripe.Account', related_name='plans',
                                editable=False, on_delete=models.PROTECT)

    stripe_id = models.CharField('Stripe ID', max_length=255, db_index=True,
                                 editable=False)

    objects = managers.PlanManager.for_queryset_class(models.query.QuerySet)()

    class Meta(object):
        unique_together = ['account', 'stripe_id']

    def __str__(self):
        return self.api_data().get('name')
