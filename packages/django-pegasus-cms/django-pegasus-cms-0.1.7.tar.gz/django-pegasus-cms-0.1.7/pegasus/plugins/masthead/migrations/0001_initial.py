# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import masthead.models
import cms.models.pluginmodel


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20140926_2347'),
    ]

    operations = [
        migrations.CreateModel(
            name='MastheadPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(primary_key=True, parent_link=True, auto_created=True, serialize=False, to='cms.CMSPlugin')),
                ('image', models.ImageField(null=True, upload_to=cms.models.pluginmodel.CMSPlugin.get_media_path, verbose_name='image', blank=True)),
                ('image_mask', models.CharField(null=True, help_text='Hex code for an image mask', validators=[masthead.models.validate_hex], max_length=7, blank=True)),
                ('columns', models.SmallIntegerField(choices=[(1, 1), (2, 2)], default=2)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
