# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from . import forms, views
from .models import (Application, ConnectedAccount, Customer, Plan,
                     StandardAccount, Subscription)
from copy import copy
from django.conf.urls import patterns, url
from django.contrib import admin
from django.http import HttpResponseRedirect


class ApplicationAdmin(admin.ModelAdmin):

    form = forms.ApplicationForm

    list_display = ['__str__', 'account']

    readonly_fields = []

    def get_readonly_fields(self, request, obj=None, **kwargs):
        readonly_fields = copy(
            super(ApplicationAdmin, self).get_readonly_fields(
                request, obj, **kwargs))
        if obj is not None:
            readonly_fields += ['account']
        return readonly_fields

admin.site.register(Application, ApplicationAdmin)


class ConnectedAccountAdmin(admin.ModelAdmin):

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


class SubscriptionInline(admin.StackedInline):

    model = Subscription

    extra = 0

    readonly_fields = ['stripe_id']

    def has_add_permission(self, *args, **kwarg):
        return False

    def has_delete_permission(self, *args, **kwarg):
        return False


class CustomerAdmin(admin.ModelAdmin):

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


class PlanAdmin(admin.ModelAdmin):

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


class StandardAccountAdmin(admin.ModelAdmin):

    exclude = ['application']

    form = forms.AccountForm

    list_display = ['__str__', 'stripe_id']

    readonly_fields = ['stripe_id']

admin.site.register(StandardAccount, StandardAccountAdmin)


class SubscriptionAdmin(admin.ModelAdmin):

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
