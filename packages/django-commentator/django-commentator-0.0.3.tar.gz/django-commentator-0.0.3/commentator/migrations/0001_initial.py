# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id',
                 models.AutoField(verbose_name='ID',
                                  serialize=False,
                                  auto_created=True,
                                  primary_key=True)),
                ('text',
                 models.TextField(null=True,
                                  verbose_name='Comment',
                                  blank=True)),
                ('raw', models.TextField(verbose_name='Raw content')),
                ('edited',
                 models.BooleanField(default=False,
                                     verbose_name='Edited')),
                ('deleted',
                 models.BooleanField(default=False,
                                     verbose_name='Deleted')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(null=True, blank=True)),
                ('path',
                 models.CharField(default=b'',
                                  max_length=255,
                                  blank=True)),
                ('author',
                 models.ForeignKey(verbose_name='User',
                                   to=settings.AUTH_USER_MODEL)),
                ('part_of', models.ForeignKey(default=None, blank=True, to='commentator.Comment', null=True,
                                              verbose_name='Parent')),
            ],
            options={
                'ordering': ('thread', 'created_at'),
                'db_table': 'commentaror_comments',
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id',
                 models.AutoField(verbose_name='ID',
                                  serialize=False,
                                  auto_created=True,
                                  primary_key=True)),
                ('object_pk', models.TextField(verbose_name='object ID')),
                ('last_message',
                 models.DateTimeField(db_index=True,
                                      null=True,
                                      blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('content_type',
                 models.ForeignKey(related_name='content_type_set_for_thread', verbose_name='content type',
                                   to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('-last_message',),
                'db_table': 'commentaror_threads',
                'verbose_name': 'Thread',
                'verbose_name_plural': 'Threads',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='comment',
            name='thread',
            field=models.ForeignKey(
                verbose_name='Thread',
                to='commentator.Thread'),
            preserve_default=True,
        ),
    ]
