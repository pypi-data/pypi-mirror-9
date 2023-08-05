# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CryptoKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('flags', models.PositiveIntegerField(help_text=b'Key flags.', verbose_name='flags')),
                ('active', models.BooleanField(help_text=b'Check to activate key.', verbose_name='active')),
                ('content', models.TextField(help_text=b'Enter the key data.', null=True, verbose_name='content', blank=True)),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
            ],
            options={
                'ordering': ['domain'],
                'db_table': 'cryptokeys',
                'verbose_name': 'crypto key',
                'verbose_name_plural': 'crypto keys',
                'get_latest_by': 'date_modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'This field is the actual domainname. This is the field that powerDNS matches to when it gets a request. The domainname should be in the format of: domainname.TLD (no trailing dot)', unique=True, max_length=255, verbose_name='name', db_index=True)),
                ('master', models.CharField(help_text=b'Enter a comma delimited list of nameservers that are master for this domain. This setting applies only to slave zones.', max_length=128, null=True, verbose_name='master', blank=True)),
                ('last_check', models.PositiveIntegerField(help_text=b'Last time this domain was checked for freshness.', max_length=11, null=True, verbose_name='last check')),
                ('type', models.CharField(default=b'NATIVE', help_text=b'Select the zone type. Native refers to native SQL replication. Master/Slave refers to DNS server based zone transfers.', max_length=6, verbose_name='type', choices=[(b'NATIVE', b'Native'), (b'MASTER', b'Master'), (b'SLAVE', b'Slave')])),
                ('notified_serial', models.PositiveIntegerField(help_text=b'The last notified serial of a master domain. This is updated from the SOA record of the domain.', max_length=11, null=True, verbose_name='notified serial')),
                ('account', models.CharField(help_text=b'Determine if a certain host is a supermaster for a certain domain name. (???)', max_length=40, null=True, verbose_name='account', blank=True)),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('created_by', models.ForeignKey(related_name='powerdns_manager_domain_created_by', verbose_name='owner username', to=settings.AUTH_USER_MODEL, help_text=b'The Django user this zone belongs to.', null=True)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'domains',
                'verbose_name': 'zone',
                'verbose_name_plural': 'zones',
                'get_latest_by': 'date_modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DomainMetadata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kind', models.CharField(help_text=b'Select a setting.', max_length=16, verbose_name='setting', choices=[(b'ALLOW-AXFR-FROM', b'ALLOW-AXFR-FROM'), (b'AXFR-MASTER-TSIG', b'AXFR-MASTER-TSIG'), (b'LUA-AXFR-SCRIPT', b'LUA-AXFR-SCRIPT'), (b'NSEC3NARROW', b'NSEC3NARROW'), (b'NSEC3PARAM', b'NSEC3PARAM'), (b'PRESIGNED', b'PRESIGNED'), (b'SOA-EDIT', b'SOA-EDIT'), (b'TSIG-ALLOW-AXFR', b'TSIG-ALLOW-AXFR')])),
                ('content', models.TextField(help_text=b'Enter the metadata.', null=True, verbose_name='content', blank=True)),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('domain', models.ForeignKey(related_name='powerdns_manager_domainmetadata_domain', verbose_name='domain', to='powerdns_manager.Domain', help_text='Select the domain this record belongs to.')),
            ],
            options={
                'ordering': ['kind'],
                'db_table': 'domainmetadata',
                'verbose_name': 'domain metadata',
                'verbose_name_plural': 'domain metadata',
                'get_latest_by': 'date_modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DynamicZone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_dynamic', models.BooleanField(help_text=b'Check to mark this zone as dynamic. An API key will be generated for you so as to be able to update the A nd AAAA records IP addresses over HTTP.', verbose_name='Dynamic zone')),
                ('api_key', models.CharField(help_text=b'The API key is generated automatically. To reset it, use the relevant action in the changelist view.', max_length=64, null=True, verbose_name='API Key')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('domain', models.ForeignKey(related_name='powerdns_manager_dynamiczone_domain', verbose_name='domain', to='powerdns_manager.Domain', help_text='Select the domain, the A and AAAA records of which might be updated dynamically over HTTP.', unique=True)),
            ],
            options={
                'ordering': ['-domain'],
                'db_table': 'dynamiczones',
                'verbose_name': 'dynamic zone',
                'verbose_name_plural': 'dynamic zones',
                'get_latest_by': 'date_modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b"Actual name of a record. Must not end in a '.' and be fully qualified - it is not relative to the name of the domain!  For example: www.test.com (no trailing dot)", max_length=255, null=True, verbose_name='name', db_index=True)),
                ('type', models.CharField(choices=[(b'SOA', b'SOA'), (b'NS', b'NS'), (b'MX', b'MX'), (b'A', b'A'), (b'AAAA', b'AAAA'), (b'CNAME', b'CNAME'), (b'PTR', b'PTR'), (b'TXT', b'TXT'), (b'SPF', b'SPF'), (b'SRV', b'SRV')], max_length=10, help_text=b'Select the type of the resource record.', null=True, verbose_name='type', db_index=True)),
                ('content', models.CharField(help_text=b"This is the 'right hand side' of a DNS record. For an A record, this is the IP address for example.", max_length=64000, null=True, verbose_name='content')),
                ('ttl', models.PositiveIntegerField(help_text=b'How long the DNS-client are allowed to remember this record. Also known as Time To Live(TTL) This value is in seconds.', max_length=11, null=True, verbose_name='TTL', blank=True)),
                ('prio', models.PositiveIntegerField(help_text=b'For MX records, this should be the priority of the mail exchanger specified.', max_length=11, null=True, verbose_name='priority')),
                ('auth', models.NullBooleanField(help_text=b"The 'auth' field should be set to '1' for data for which the zone itself is authoritative, which includes the SOA record and its own NS records. The 'auth' field should be 0 however for NS records which are used for delegation, and also for any glue (A, AAAA) records present for this purpose. Do note that the DS record for a secure delegation should be authoritative!", verbose_name='authoritative')),
                ('ordername', models.CharField(help_text=b'http://doc.powerdns.com/dnssec-modes.html#dnssec-direct-database', max_length=255, null=True, verbose_name='ordername', db_index=True)),
                ('change_date', models.PositiveIntegerField(help_text=b'Timestamp for the last update. This is used by PowerDNS internally.', max_length=11, null=True, verbose_name='change date')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('domain', models.ForeignKey(related_name='powerdns_manager_record_domain', verbose_name='domain', to='powerdns_manager.Domain', help_text='Select the domain this record belongs to.')),
            ],
            options={
                'get_latest_by': 'date_modified',
                'ordering': ['name', 'type'],
                'verbose_name_plural': 'records',
                'db_table': 'records',
                'verbose_name': 'record',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SuperMaster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.GenericIPAddressField(help_text=b'IP address for supermaster (IPv4 or IPv6).', unique=True, verbose_name='IP address')),
                ('nameserver', models.CharField(help_text=b'Hostname of the supermaster.', unique=True, max_length=255, verbose_name='nameserver')),
                ('account', models.CharField(help_text=b'Account name (???)', max_length=40, null=True, verbose_name='account', blank=True)),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
            ],
            options={
                'ordering': ['nameserver'],
                'db_table': 'supermasters',
                'verbose_name': 'supermaster',
                'verbose_name_plural': 'supermasters',
                'get_latest_by': 'date_modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TsigKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Enter a name for the key.', max_length=255, verbose_name='name')),
                ('algorithm', models.CharField(help_text=b'Select hashing algorithm.', max_length=50, verbose_name='algorithm', choices=[(b'hmac-md5', b'hmac-md5')])),
                ('secret', models.CharField(help_text=b'Enter the shared secret.', max_length=255, verbose_name='secret')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('created_by', models.ForeignKey(related_name='powerdns_manager_tsigkey_created_by', verbose_name='created by', to=settings.AUTH_USER_MODEL, help_text=b'The Django user this TSIG key belongs to.', null=True)),
            ],
            options={
                'get_latest_by': 'date_modified',
                'ordering': ['name'],
                'verbose_name_plural': 'TSIG Keys',
                'db_table': 'tsigkeys',
                'verbose_name': 'TSIG Key',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ZoneTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Enter a name for the template.', max_length=100, verbose_name='name')),
                ('content', models.TextField(help_text=b'Enter the template content. The placeholder #origin# is expanded to the origin of the zone to which the template is applied.', null=True, verbose_name='content', blank=True)),
                ('notes', models.TextField(help_text=b'Space for notes about the template.', null=True, verbose_name='notes', blank=True)),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='Last Modified')),
                ('created_by', models.ForeignKey(related_name='powerdns_manager_zonetemplate_created_by', verbose_name='template creator', to=settings.AUTH_USER_MODEL, help_text=b'The Django user this template belongs to.')),
            ],
            options={
                'get_latest_by': 'date_modified',
                'ordering': ['name', 'date_modified'],
                'verbose_name_plural': 'templates',
                'db_table': 'zonetemplates',
                'verbose_name': 'template',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='zonetemplate',
            unique_together=set([('name', 'created_by')]),
        ),
        migrations.AlterUniqueTogether(
            name='tsigkey',
            unique_together=set([('name', 'algorithm')]),
        ),
        migrations.AlterIndexTogether(
            name='record',
            index_together=set([('domain', 'ordername'), ('name', 'type')]),
        ),
        migrations.AddField(
            model_name='cryptokey',
            name='domain',
            field=models.ForeignKey(related_name='powerdns_manager_cryptokey_domain', verbose_name='domain', to='powerdns_manager.Domain', help_text='Select the domain this record belongs to.'),
            preserve_default=True,
        ),
    ]
