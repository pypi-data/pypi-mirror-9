# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns_manager', '0002_auto_20150114_1403'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='disabled',
            field=models.BooleanField(default=False, help_text=b'Enable or disable this Resource Record.', verbose_name='disabled'),
            preserve_default=True,
        ),
    ]
