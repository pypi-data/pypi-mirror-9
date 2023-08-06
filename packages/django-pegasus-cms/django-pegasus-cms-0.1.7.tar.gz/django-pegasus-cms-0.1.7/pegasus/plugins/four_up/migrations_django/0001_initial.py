# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '__first__'),
        ('cms', '0003_auto_20140926_2347'),
    ]

    operations = [
        migrations.CreateModel(
            name='FourUpPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(to='cms.CMSPlugin', primary_key=True, parent_link=True, serialize=False, auto_created=True)),
                ('title', models.CharField(max_length=255)),
                ('size', models.IntegerField(default=4)),
                ('backfill_method', models.CharField(max_length=20, default='most_recent', choices=[('most_recent', 'Most Recent')])),
                ('backfill_article_type', models.ForeignKey(to='content.ArticleType', blank=True, null=True)),
                ('backfill_issue', models.ForeignKey(to='content.Issue', blank=True, null=True)),
                ('backfill_topic', models.ForeignKey(to='content.Topic', blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
    ]
