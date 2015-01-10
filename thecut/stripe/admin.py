# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from . import forms, views
from .models import (Application, ConnectedAccount, Charge, Customer, Plan,
                     StandardAccount, Subscription)
from copy import copy
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.admin.utils import model_ngettext
from django.http import HttpResponseRedirect
from django.utils.translation import ungettext


class StripeAPIActionMixin(object):

    actions = ['clear_api_cache']

    def clear_api_cache(self, request, queryset):
        for instance in queryset:
            instance.api(clear=True)
        count = len(queryset)
        message = 'Cleared API cache for {count} {items}.'.format(
            count=count, items=model_ngettext(self.opts, count))
        self.message_user(request, message)

    clear_api_cache.short_description = ('Clear API cache for selected '
                                         '%(verbose_name_plural)s')


class ApplicationAdmin(StripeAPIActionMixin, admin.ModelAdmin):

    form = forms.ApplicationForm

    list_display = ['__str__', 'account', 'callback_uri']

    readonly_fields = []

    def _get_callback_uri(self, request):
        url = reverse(
            '{0}:stripe_connect_oauth2_callback'.format(self.admin_site.name))
        return request.build_absolute_uri(url)

    @admin.options.csrf_protect_m
    def changelist_view(self, request, *args, **kwargs):
        self._callback_uri = self._get_callback_uri(request)
        return super(ApplicationAdmin, self).changelist_view(request, *args,
                                                             **kwargs)

    def callback_uri(self, *args, **kwargs):
        return self._callback_uri
    callback_uri.short_description = 'Callback URI'

    def get_readonly_fields(self, request, obj=None, **kwargs):
        readonly_fields = copy(
            super(ApplicationAdmin, self).get_readonly_fields(
                request, obj, **kwargs))
        if obj is not None:
            readonly_fields += ['account']
        return readonly_fields

admin.site.register(Application, ApplicationAdmin)


class ChargeAdmin(StripeAPIActionMixin, admin.ModelAdmin):

    list_display = ['__str__', 'stripe_id', 'account', 'application']

    list_filter = ['account', 'account__application']

    readonly_fields = ['stripe_id']

    def application(self, obj):
        return obj.account.application

    def get_queryset(self, *args, **kwargs):
        queryset = super(ChargeAdmin, self).get_queryset(*args, **kwargs)
        return queryset.select_related('account', 'account__application')

    def has_add_permission(self, *args, **kwargs):
        return False

admin.site.register(Charge, ChargeAdmin)


class ConnectedAccountAdmin(StripeAPIActionMixin, admin.ModelAdmin):

    exclude = ['_secret_key', '_publishable_key']

    form = forms.AccountForm

    list_display = ['__str__', 'stripe_id', 'application']

    readonly_fields = ['stripe_id']

    def get_readonly_fields(self, request, obj=None, **kwargs):
        readonly_fields = copy(
            super(ConnectedAccountAdmin, self).get_readonly_fields(
                request, obj, **kwargs))
        if obj is not None:
            readonly_fields += ['application']
        return readonly_fields

    def get_urls(self):
        urlpatterns = patterns(
            'thecut.stripe.views',
            url(r'^(?P<pk>\d+)/oauth2/request$',
                views.OAuth2RequestTokenView.as_view(),
                name='stripe_connect_oauth2_request_token'),
            url(r'^oauth2/callback$',
                views.OAuth2CallbackView.as_view(),
                name='stripe_connect_oauth2_callback'),
        )
        urlpatterns += super(ConnectedAccountAdmin, self).get_urls()
        return urlpatterns

    def response_add(self, request, obj, **kwargs):
        # Redirect to request oauth2 credentials
        return HttpResponseRedirect(
            request.build_absolute_uri('../{0}/oauth2/request'.format(obj.pk)))

admin.site.register(ConnectedAccount, ConnectedAccountAdmin)


class SubscriptionInline(StripeAPIActionMixin, admin.StackedInline):

    model = Subscription

    extra = 0

    readonly_fields = ['stripe_id']

    def has_add_permission(self, *args, **kwarg):
        return False

    def has_delete_permission(self, *args, **kwarg):
        return False


class CustomerAdmin(StripeAPIActionMixin, admin.ModelAdmin):

    inlines = [SubscriptionInline]

    list_display = ['__str__', 'stripe_id', 'account', 'application']

    list_filter = ['account', 'account__application']

    readonly_fields = ['stripe_id']

    def application(self, obj):
        return obj.account.application

    def get_queryset(self, *args, **kwargs):
        queryset = super(CustomerAdmin, self).get_queryset(*args, **kwargs)
        return queryset.select_related('account', 'account__application')

    def has_add_permission(self, *args, **kwargs):
        return False

admin.site.register(Customer, CustomerAdmin)


class PlanAdmin(StripeAPIActionMixin, admin.ModelAdmin):

    list_display = ['__str__', 'stripe_id', 'account', 'application']

    list_filter = ['account', 'account__application']

    readonly_fields = ['stripe_id']

    def application(self, obj):
        return obj.account.application

    def get_queryset(self, *args, **kwargs):
        queryset = super(PlanAdmin, self).get_queryset(*args, **kwargs)
        return queryset.select_related('account', 'account__application')

    def has_add_permission(self, *args, **kwargs):
        return False

admin.site.register(Plan, PlanAdmin)


class StandardAccountAdmin(StripeAPIActionMixin, admin.ModelAdmin):

    exclude = ['application']

    form = forms.AccountForm

    list_display = ['__str__', 'stripe_id']

    readonly_fields = ['stripe_id']

admin.site.register(StandardAccount, StandardAccountAdmin)


class SubscriptionAdmin(StripeAPIActionMixin, admin.ModelAdmin):

    list_display = ['__str__', 'stripe_id', 'customer', 'account',
                    'application']

    list_filter = ['plan', 'customer', 'account', 'account__application']

    readonly_fields = ['stripe_id']

    def application(self, obj):
        return obj.account.application

    def get_queryset(self, *args, **kwargs):
        queryset = super(SubscriptionAdmin, self).get_queryset(*args, **kwargs)
        return queryset.select_related('plan', 'customer', 'account',
                                       'account__application')

    def has_add_permission(self, *args, **kwargs):
        return False

admin.site.register(Subscription, SubscriptionAdmin)
