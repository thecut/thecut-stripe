# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from .forms import AccountForm, ApplicationForm
from .models import Account, Application, Customer, Plan
from copy import copy
from django.contrib import admin


class AccountAdmin(admin.ModelAdmin):

    form = AccountForm

    list_display = ['__str__', 'stripe_id', 'application']

    readonly_fields = ['stripe_id', '_api_data_updated_at']

    def get_fieldsets(self, request, obj=None, **kwargs):
        fieldsets = super(AccountAdmin, self).get_fieldsets(request, obj=obj,
                                                            **kwargs)
        if obj is not None and obj.application:
            fieldsets = [
                (None, {'fields': self.get_readonly_fields(request, obj)})]
        return fieldsets

    def get_readonly_fields(self, request, obj=None, **kwargs):
        readonly_fields = copy(super(AccountAdmin, self).get_readonly_fields(
                               request, obj, **kwargs))
        if obj is not None and obj.application:
            readonly_fields += ['application']
        return readonly_fields

admin.site.register(Account, AccountAdmin)


class ApplicationAdmin(admin.ModelAdmin):

    form = ApplicationForm

    list_display = ['__str__', 'account']

admin.site.register(Application, ApplicationAdmin)


class CustomerAdmin(admin.ModelAdmin):

    list_display = ['__str__', 'stripe_id', 'account', 'application']

    list_filter = ['account', 'account__application']

    readonly_fields = ['stripe_id', '_api_data_updated_at']

    def application(self, obj):
        return obj.account.application

    def get_queryset(self, *args, **kwargs):
        queryset = super(CustomerAdmin, self).get_queryset(*args, **kwargs)
        return queryset.select_related('account', 'account__application')

admin.site.register(Customer, CustomerAdmin)


class PlanAdmin(admin.ModelAdmin):

    list_display = ['__str__', 'stripe_id', 'account', 'application']

    list_filter = ['account', 'account__application']

    readonly_fields = ['stripe_id', '_api_data_updated_at']

    def application(self, obj):
        return obj.account.application

    def get_queryset(self, *args, **kwargs):
        queryset = super(PlanAdmin, self).get_queryset(*args, **kwargs)
        return queryset.select_related('account', 'account__application')

admin.site.register(Plan, PlanAdmin)
