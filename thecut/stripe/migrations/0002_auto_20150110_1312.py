# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stripe', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_id', models.CharField(verbose_name='Stripe ID', max_length=255, editable=False, db_index=True)),
                ('account', models.ForeignKey(related_name='charges', on_delete=django.db.models.deletion.PROTECT, editable=False, to='stripe.Account')),
                ('customer', models.ForeignKey(related_name='charges', on_delete=django.db.models.deletion.PROTECT, editable=False, to='stripe.Customer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='charge',
            unique_together=set([('account', 'stripe_id')]),
        ),
    ]
