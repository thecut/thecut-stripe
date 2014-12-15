# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from ..forms import CardForm
from django.forms import Form
from django.http import Http404
from django.views import generic
import stripe


class CustomerMixin(object):

    def get_context_data(self, *args, **kwargs):
        context_data = super(CustomerMixin, self).get_context_data(*args,
                                                                   **kwargs)
        context_data.update({'stripe_customer': self.get_stripe_customer()})
        return context_data

    def get_stripe_customer(self):
        raise NotImplementedError('You should override this method to provide '
                                  'the stripe customer instance.')


class CreateView(CustomerMixin, generic.FormView):

    form_class = CardForm

    def form_valid(self, form, *args, **kwargs):
        form.save(stripe_customer=self.get_stripe_customer())
        return super(CreateView, self).form_valid(form, *args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super(CreateView, self).get_form_kwargs(*args, **kwargs)
        form_kwargs.update({
            'stripe_publishable_key': self.get_stripe_publishable_key()})
        return form_kwargs

    def get_stripe_publishable_key(self):
        return self.get_stripe_customer().account.publishable_key


class EditMixin(CustomerMixin, generic.FormView):

    form_class = Form

    def get_card(self):
        stripe_customer = self.get_stripe_customer()
        try:
            card = stripe_customer.api().cards.retrieve(self.kwargs['card_id'])
        except stripe.error.InvalidRequestError:
            raise Http404('Card not found.')
        return card

    def get_context_data(self, *args, **kwargs):
        context_data = super(EditMixin, self).get_context_data(*args, **kwargs)
        context_data.update({'card': self.get_card()})
        return context_data


class DefaultView(EditMixin):

    def form_valid(self, form, *args, **kwargs):
        stripe_customer = self.get_stripe_customer()
        api = stripe_customer.api()
        api.default_card = self.get_card().id
        api.save()
        stripe_customer.api(refresh=True)  # Refresh API cache
        return super(DefaultView, self).form_valid(form, *args, **kwargs)


class DeleteView(EditMixin):

    def form_valid(self, form, *args, **kwargs):
        self.get_card().delete()
        self.get_stripe_customer().api(refresh=True)  # Refresh API cache
        return super(DeleteView, self).form_valid(form, *args, **kwargs)
