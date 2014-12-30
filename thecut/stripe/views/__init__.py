# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from ..models import ConnectedAccount
from django.contrib.admin.options import csrf_protect_m
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views import generic


class OAuth2RequestTokenView(generic.detail.SingleObjectMixin, generic.View):

    model = ConnectedAccount

    @csrf_protect_m
    @method_decorator(permission_required('stripe.change_connectedaccount'))
    def dispatch(self, *args, **kwargs):
        return super(OAuth2RequestTokenView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.request.session['oauth2_stripe_connectedaccount'] = self.object.pk
        self.request.session.modified = True
        authorize_url = self.object.application.get_connect_authorize_url(
            redirect_uri=self.get_redirect_url())
        return HttpResponseRedirect(authorize_url)

    def get_redirect_url(self):
        return self.request.build_absolute_uri('../../oauth2/callback')  # TODO


class OAuth2CallbackView(generic.View):

    object = None

    @csrf_protect_m
    @method_decorator(permission_required('stripe.change_connectedaccount'))
    def dispatch(self, *args, **kwargs):
        return super(OAuth2CallbackView, self).dispatch(*args, **kwargs)

    def get(self, *args, **kwargs):
        account_pk = self.request.session.pop('oauth2_stripe_connectedaccount',
                                              None)
        try:
            self.object = ConnectedAccount.objects.get(pk=account_pk)
        except ConnectedAccount.DoesNotExist:
            self.object = None
        code = self.request.GET.get('code', None)
        self.request.session.modified = True

        if None in [self.object, code]:
            # TODO: Error handling
            return HttpResponseBadRequest()
        else:
            self.object.store_credentials(code)
            return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return '../{0}/'.format(self.object.pk)  # TODO
