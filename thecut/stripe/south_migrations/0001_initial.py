# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AccountOAuth2Credentials'
        db.create_table(u'stripe_accountoauth2credentials', (
            ('id', self.gf('django.db.models.fields.related.OneToOneField')(related_name=u'_oauth2_credentials', unique=True, primary_key=True, to=orm['stripe.Account'])),
            ('credentials', self.gf('oauth2client.django_orm.CredentialsField')(null=True)),
        ))
        db.send_create_signal(u'stripe', ['AccountOAuth2Credentials'])

        # Adding model 'Account'
        db.create_table(u'stripe_account', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('application', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'accounts', null=True, on_delete=models.PROTECT, to=orm['stripe.Application'])),
            ('_secret_key', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
            ('_publishable_key', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal(u'stripe', ['Account'])

        # Adding model 'Application'
        db.create_table(u'stripe_application', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'applications', on_delete=models.PROTECT, to=orm['stripe.Account'])),
            ('client_id', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'stripe', ['Application'])

        # Adding model 'Charge'
        db.create_table(u'stripe_charge', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'charges', on_delete=models.PROTECT, to=orm['stripe.Account'])),
            ('stripe_id', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'charges', on_delete=models.PROTECT, to=orm['stripe.Customer'])),
        ))
        db.send_create_signal(u'stripe', ['Charge'])

        # Adding unique constraint on 'Charge', fields ['account', 'stripe_id']
        db.create_unique(u'stripe_charge', ['account_id', 'stripe_id'])

        # Adding model 'Customer'
        db.create_table(u'stripe_customer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'customers', on_delete=models.PROTECT, to=orm['stripe.Account'])),
            ('stripe_id', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal(u'stripe', ['Customer'])

        # Adding unique constraint on 'Customer', fields ['account', 'stripe_id']
        db.create_unique(u'stripe_customer', ['account_id', 'stripe_id'])

        # Adding model 'Plan'
        db.create_table(u'stripe_plan', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'plans', on_delete=models.PROTECT, to=orm['stripe.Account'])),
            ('stripe_id', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal(u'stripe', ['Plan'])

        # Adding unique constraint on 'Plan', fields ['account', 'stripe_id']
        db.create_unique(u'stripe_plan', ['account_id', 'stripe_id'])

        # Adding model 'Subscription'
        db.create_table(u'stripe_subscription', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'subscriptions', on_delete=models.PROTECT, to=orm['stripe.Account'])),
            ('stripe_id', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'subscriptions', on_delete=models.PROTECT, to=orm['stripe.Customer'])),
            ('plan', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'subscriptions', on_delete=models.PROTECT, to=orm['stripe.Plan'])),
        ))
        db.send_create_signal(u'stripe', ['Subscription'])

        # Adding unique constraint on 'Subscription', fields ['account', 'stripe_id']
        db.create_unique(u'stripe_subscription', ['account_id', 'stripe_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Subscription', fields ['account', 'stripe_id']
        db.delete_unique(u'stripe_subscription', ['account_id', 'stripe_id'])

        # Removing unique constraint on 'Plan', fields ['account', 'stripe_id']
        db.delete_unique(u'stripe_plan', ['account_id', 'stripe_id'])

        # Removing unique constraint on 'Customer', fields ['account', 'stripe_id']
        db.delete_unique(u'stripe_customer', ['account_id', 'stripe_id'])

        # Removing unique constraint on 'Charge', fields ['account', 'stripe_id']
        db.delete_unique(u'stripe_charge', ['account_id', 'stripe_id'])

        # Deleting model 'AccountOAuth2Credentials'
        db.delete_table(u'stripe_accountoauth2credentials')

        # Deleting model 'Account'
        db.delete_table(u'stripe_account')

        # Deleting model 'Application'
        db.delete_table(u'stripe_application')

        # Deleting model 'Charge'
        db.delete_table(u'stripe_charge')

        # Deleting model 'Customer'
        db.delete_table(u'stripe_customer')

        # Deleting model 'Plan'
        db.delete_table(u'stripe_plan')

        # Deleting model 'Subscription'
        db.delete_table(u'stripe_subscription')


    models = {
        u'stripe.account': {
            'Meta': {'object_name': 'Account'},
            '_publishable_key': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            '_secret_key': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'application': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'accounts'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['stripe.Application']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'stripe.accountoauth2credentials': {
            'Meta': {'object_name': 'AccountOAuth2Credentials'},
            'credentials': ('oauth2client.django_orm.CredentialsField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'_oauth2_credentials'", 'unique': 'True', 'primary_key': 'True', 'to': u"orm['stripe.Account']"})
        },
        u'stripe.application': {
            'Meta': {'object_name': 'Application'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'applications'", 'on_delete': 'models.PROTECT', 'to': u"orm['stripe.Account']"}),
            'client_id': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'stripe.charge': {
            'Meta': {'unique_together': "([u'account', u'stripe_id'],)", 'object_name': 'Charge'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'charges'", 'on_delete': 'models.PROTECT', 'to': u"orm['stripe.Account']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'charges'", 'on_delete': 'models.PROTECT', 'to': u"orm['stripe.Customer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stripe_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'stripe.customer': {
            'Meta': {'unique_together': "([u'account', u'stripe_id'],)", 'object_name': 'Customer'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'customers'", 'on_delete': 'models.PROTECT', 'to': u"orm['stripe.Account']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stripe_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'stripe.plan': {
            'Meta': {'unique_together': "([u'account', u'stripe_id'],)", 'object_name': 'Plan'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'plans'", 'on_delete': 'models.PROTECT', 'to': u"orm['stripe.Account']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'stripe_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        u'stripe.subscription': {
            'Meta': {'unique_together': "([u'account', u'stripe_id'],)", 'object_name': 'Subscription'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'subscriptions'", 'on_delete': 'models.PROTECT', 'to': u"orm['stripe.Account']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'subscriptions'", 'on_delete': 'models.PROTECT', 'to': u"orm['stripe.Customer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'subscriptions'", 'on_delete': 'models.PROTECT', 'to': u"orm['stripe.Plan']"}),
            'stripe_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        }
    }

    complete_apps = ['stripe']