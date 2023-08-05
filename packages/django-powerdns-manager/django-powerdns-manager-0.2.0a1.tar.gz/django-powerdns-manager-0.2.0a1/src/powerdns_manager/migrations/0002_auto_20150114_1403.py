# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cryptokey',
            name='active',
            field=models.BooleanField(default=False, help_text=b'Check to activate key.', verbose_name='active'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='dynamiczone',
            name='is_dynamic',
            field=models.BooleanField(default=False, help_text=b'Check to mark this zone as dynamic. An API key will be generated for you so as to be able to update the A nd AAAA records IP addresses over HTTP.', verbose_name='Dynamic zone'),
            preserve_default=True,
        ),
    ]
