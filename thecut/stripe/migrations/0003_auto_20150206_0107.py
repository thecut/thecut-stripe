# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stripe', '0002_auto_20150110_1312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charge',
            name='customer',
            field=models.ForeignKey(related_name='charges', on_delete=django.db.models.deletion.PROTECT, blank=True, editable=False, to='stripe.Customer', null=True),
            preserve_default=True,
        ),
    ]
