# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from model_utils.managers import PassThroughManager
import stripe


class CustomerManager(PassThroughManager):

    def sync(self):
        response = stripe.Customer.all(api_key=self.instance.secret_key,
                                       include=['total_count'])['data']
        for data in response:
            self.get_or_create(stripe_id=data['id'],
                               defaults={'_api_data': data})


class PlanManager(PassThroughManager):

    def sync(self):
        response = stripe.Plan.all(api_key=self.instance.secret_key,
                                   include=['total_count'])['data']
        for data in response:
            self.get_or_create(stripe_id=data['id'],
                               defaults={'_api_data': data})
