# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramPluginModel',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(auto_created=True, parent_link=True, to='cms.CMSPlugin', primary_key=True, serialize=False)),
                ('title', models.CharField(null=True, max_length=100, verbose_name='title', blank=True)),
                ('client_id', models.CharField(max_length=100, verbose_name='client ID')),
                ('user_id', models.IntegerField(verbose_name='user ID')),
                ('pictures', models.IntegerField(verbose_name='pictures', help_text='Number of pictures displayed.')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
