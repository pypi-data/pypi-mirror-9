# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LoginAttempt',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(verbose_name='username', null=True, blank=True, max_length=255)),
                ('password', models.CharField(verbose_name='password', null=True, blank=True, max_length=255)),
                ('ip_address', models.IPAddressField(verbose_name='ip address', null=True, blank=True)),
                ('session_key', models.CharField(verbose_name='session key', null=True, blank=True, max_length=50)),
                ('user_agent', models.TextField(verbose_name='user-agent', null=True, blank=True)),
                ('timestamp', models.DateTimeField(verbose_name='timestamp', auto_now_add=True)),
                ('path', models.TextField(verbose_name='path', null=True, blank=True)),
            ],
            options={
                'verbose_name': 'login attempt',
                'ordering': ('timestamp',),
                'verbose_name_plural': 'login attempts',
            },
            bases=(models.Model,),
        ),
    ]
