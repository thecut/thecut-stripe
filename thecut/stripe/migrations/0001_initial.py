# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import oauth2client.django_orm


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('_secret_key', models.TextField(default='', verbose_name='secret key', blank=True)),
                ('_publishable_key', models.TextField(default='', verbose_name='publishable key', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AccountOAuth2Credentials',
            fields=[
                ('id', models.OneToOneField(related_name='_oauth2_credentials', primary_key=True, serialize=False, to='stripe.Account')),
                ('credentials', oauth2client.django_orm.CredentialsField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('client_id', models.TextField(verbose_name='Client ID')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_id', models.CharField(verbose_name='Stripe ID', max_length=255, editable=False, db_index=True)),
                ('account', models.ForeignKey(related_name='customers', on_delete=django.db.models.deletion.PROTECT, editable=False, to='stripe.Account')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_id', models.CharField(verbose_name='Stripe ID', max_length=255, editable=False, db_index=True)),
                ('account', models.ForeignKey(related_name='plans', on_delete=django.db.models.deletion.PROTECT, editable=False, to='stripe.Account')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_id', models.CharField(verbose_name='Stripe ID', max_length=255, editable=False, db_index=True)),
                ('account', models.ForeignKey(related_name='subscriptions', on_delete=django.db.models.deletion.PROTECT, editable=False, to='stripe.Account')),
                ('customer', models.ForeignKey(related_name='subscriptions', on_delete=django.db.models.deletion.PROTECT, editable=False, to='stripe.Customer')),
                ('plan', models.ForeignKey(related_name='subscriptions', on_delete=django.db.models.deletion.PROTECT, editable=False, to='stripe.Plan')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='subscription',
            unique_together=set([('account', 'stripe_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='plan',
            unique_together=set([('account', 'stripe_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='customer',
            unique_together=set([('account', 'stripe_id')]),
        ),
        migrations.AddField(
            model_name='account',
            name='application',
            field=models.ForeignKey(related_name='accounts', on_delete=django.db.models.deletion.PROTECT, to='stripe.Application', null=True),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='ConnectedAccount',
            fields=[
            ],
            options={
                'abstract': False,
                'proxy': True,
            },
            bases=('stripe.account',),
        ),
        migrations.CreateModel(
            name='StandardAccount',
            fields=[
            ],
            options={
                'abstract': False,
                'proxy': True,
            },
            bases=('stripe.account',),
        ),
        migrations.AddField(
            model_name='application',
            name='account',
            field=models.ForeignKey(related_name='applications', on_delete=django.db.models.deletion.PROTECT, to='stripe.StandardAccount'),
            preserve_default=True,
        ),
    ]
