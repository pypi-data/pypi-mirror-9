# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns_manager', '0003_record_disabled'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Enter a name for this comment.', max_length=255, verbose_name='name')),
                ('type', models.CharField(help_text=b'Select the type of this comment.', max_length=10, verbose_name='type')),
                ('modified_at', models.PositiveIntegerField(help_text=b'Timestamp for the last modification time.', max_length=11, verbose_name='modified at')),
                ('account', models.CharField(help_text=b'Account name (???)', max_length=40, verbose_name='account')),
                ('comment', models.CharField(help_text=b'Comment body.', max_length=64000, verbose_name='comment')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('domain', models.ForeignKey(related_name='powerdns_manager_comment_domain', verbose_name='domain', to='powerdns_manager.Domain', help_text='Select the domain this comment belongs to.')),
            ],
            options={
                'get_latest_by': 'date_modified',
                'ordering': ['type'],
                'verbose_name_plural': 'comments',
                'db_table': 'comments',
                'verbose_name': 'comment',
            },
            bases=(models.Model,),
        ),
        migrations.AlterIndexTogether(
            name='comment',
            index_together=set([('name', 'type'), ('domain', 'modified_at')]),
        ),
    ]
