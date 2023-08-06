# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns_manager', '0004_auto_20150114_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='domain',
            name='date_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last Modified', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='record',
            name='date_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='Last Modified', null=True),
            preserve_default=True,
        ),
    ]
