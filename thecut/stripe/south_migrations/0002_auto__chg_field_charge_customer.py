# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Charge.customer'
        db.alter_column(u'stripe_charge', 'customer_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.PROTECT, to=orm['stripe.Customer']))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Charge.customer'
        raise RuntimeError("Cannot reverse this migration. 'Charge.customer' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Charge.customer'
        db.alter_column(u'stripe_charge', 'customer_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.PROTECT, to=orm['stripe.Customer']))

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
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "u'charges'", 'null': 'True', 'on_delete': 'models.PROTECT', 'to': u"orm['stripe.Customer']"}),
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