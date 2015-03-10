# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from .models import Account, Application
from .widgets import NamelessTextInput
from django import forms
from django.core.exceptions import ImproperlyConfigured


def _strip_data(data):
    return data.strip()


class AccountForm(forms.ModelForm):

    class Meta(object):
        fields = ['_secret_key', '_publishable_key', 'application']
        model = Account
        widgets = {'_secret_key': forms.TextInput(),
                   '_publishable_key': forms.TextInput()}

    def clean__secret_key(self):
        return _strip_data(self.cleaned_data.get('_secret_key', ''))

    def clean__publishable_key(self):
        return _strip_data(self.cleaned_data.get('_publishable_key', ''))


class ApplicationForm(forms.ModelForm):

    class Meta(object):
        fields = ['account', 'client_id']
        model = Application
        widgets = {'client_id': forms.TextInput()}

    def clean_client_id(self):
        return _strip_data(self.cleaned_data.get('client_id', ''))


class CardForm(forms.Form):
    """Form for generating card tokens (using stripe js)."""

    stripe_token = forms.CharField(widget=forms.HiddenInput)

    number = forms.CharField(
        label='Number', required=False,
        widget=NamelessTextInput(attrs={'autocomplete': 'off',
                                        'data-stripe': 'number',
                                        'inputmode': 'numeric',
                                        'pattern': '[0-9]{13,16}',
                                        'maxlength': 16,
                                        'minlength': 13,
                                        'required': 'required',
                                        'size': 16,
                                        'spellcheck': 'false'}))

    expiry_month = forms.CharField(
        label='Expiry', required=False,
        widget=NamelessTextInput(attrs={'autocomplete': 'off',
                                        'data-stripe': 'exp-month',
                                        'inputmode': 'numeric',
                                        'pattern': '[0-9]{1,2}',
                                        'maxlength': 2,
                                        'minlength': 1,
                                        'required': 'required',
                                        'size': 2,
                                        'spellcheck': 'false'}))

    expiry_year = forms.CharField(
        label='', required=False,
        widget=NamelessTextInput(attrs={'autocomplete': 'off',
                                        'data-stripe': 'exp-year',
                                        'inputmode': 'numeric',
                                        'pattern': '[0-9]{2}',
                                        'maxlength': 2,
                                        'minlength': 2,
                                        'required': 'required',
                                        'size': 2,
                                        'spellcheck': 'false'}))

    cvc = forms.CharField(
        label='CVC', required=False,
        widget=NamelessTextInput(attrs={'autocomplete': 'off',
                                        'data-stripe': 'cvc',
                                        'inputmode': 'numeric',
                                        'pattern': '[0-9]{3,4}',
                                        'maxlength': 4,
                                        'minlength': 3,
                                        'required': 'required',
                                        'size': 4,
                                        'spellcheck': 'false'}))

    set_default = forms.BooleanField(label='Set as default', required=False,
                                     initial=True)

    class Media(object):
        # Also requires jQuery
        js = ['https://js.stripe.com/v2/', 'stripe/cardForm.js']

    def __init__(self, stripe_publishable_key, **kwargs):
        super(CardForm, self).__init__(**kwargs)
        self.fields['stripe_token'].widget.attrs.update(
            {'data-stripe-publishable-key': stripe_publishable_key})

    def clean(self, *args, **kwargs):
        if any([self.cleaned_data['number'], self.cleaned_data['expiry_month'],
                self.cleaned_data['expiry_year'], self.cleaned_data['cvc']]):
            raise ImproperlyConfigured(
                'You should *never* be processing data from card fields in '
                'this form!')
        # This is required for Django 1.6 (but optional in 1.7)
        return self.cleaned_data

    def get_stripe_customer(self):
        raise NotImplementedError('You should override this method, if you '
                                  'are not providing stripe_customer when '
                                  'calling save.')

    def save(self, stripe_customer=None):
        if stripe_customer is None:
            stripe_customer = self.get_stripe_customer()

        # Save card to customer
        card = stripe_customer.api().sources.create(
            card=self.cleaned_data['stripe_token'])

        # Set as default card
        if self.cleaned_data['set_default']:
            api = stripe_customer.api()
            api.default_source = card.id
            api.save()
            stripe_customer.api(refresh=True)  # Refresh API cache

        return card
