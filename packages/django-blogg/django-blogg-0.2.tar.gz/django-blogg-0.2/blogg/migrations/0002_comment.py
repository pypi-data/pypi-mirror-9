# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blogg', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('content', models.TextField(max_length=1000L)),
                ('author', models.CharField(default=b'Anonymous', max_length=100, blank=True)),
                ('ip_address', models.GenericIPAddressField(null=True, blank=True)),
                ('user_agent', models.CharField(max_length=500L, blank=True)),
                ('published', models.BooleanField(default=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('post', models.ForeignKey(related_name='comments', to='blogg.Post')),
            ],
            options={
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
    ]
