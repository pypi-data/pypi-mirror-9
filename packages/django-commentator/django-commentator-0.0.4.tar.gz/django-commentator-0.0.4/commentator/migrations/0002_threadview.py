# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('commentator', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThreadView',
            fields=[
                ('id',
                 models.AutoField(verbose_name='ID',
                                  serialize=False,
                                  auto_created=True,
                                  primary_key=True)),
                ('timestamp',
                 models.DateTimeField(db_index=True,
                                      null=True,
                                      blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('thread',
                 models.ForeignKey(verbose_name='Thread',
                                   to='commentator.Thread')),
                ('user',
                 models.ForeignKey(verbose_name='User',
                                   to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('thread', 'created_at'),
                'db_table': 'commentaror_threadview',
                'verbose_name': 'View',
                'verbose_name_plural': 'Views',
            },
            bases=(models.Model,),
        ),
    ]
