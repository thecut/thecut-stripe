# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from .models import Account, Application
from django import forms


def _strip_data(data):
    return data.strip()


class AccountForm(forms.ModelForm):

    class Meta(object):
        fields = ['_secret_key', 'publishable_key', 'application']
        model = Account
        widgets = {'_secret_key': forms.TextInput(),
                   'publishable_key': forms.TextInput()}

    def clean__secret_key(self):
        return _strip_data(self.cleaned_data.get('_secret_key', ''))

    def clean_publishable_key(self):
        return _strip_data(self.cleaned_data.get('publishable_key', ''))


class ApplicationForm(forms.ModelForm):

    class Meta(object):
        fields = ['account', 'client_id']
        model = Application
        widgets = {'client_id': forms.TextInput()}

    def clean_client_id(self):
        return _strip_data(self.cleaned_data.get('client_id', ''))
