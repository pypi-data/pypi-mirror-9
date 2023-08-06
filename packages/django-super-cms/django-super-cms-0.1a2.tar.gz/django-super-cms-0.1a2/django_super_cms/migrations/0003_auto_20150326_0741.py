# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_super_cms', '0002_auto_20150325_0215'),
    ]

    operations = [
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(null=True, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='config name')),
                ('value', models.CharField(max_length=255, null=True, verbose_name='config value', blank=True)),
            ],
            options={
                'verbose_name': 'configuration',
                'verbose_name_plural': 'configurations',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='post',
            name='status',
            field=models.IntegerField(default=0, verbose_name='post status', choices=[(0, b'show'), (1, b'hide'), (2, b'deleted')]),
            preserve_default=True,
        ),
    ]
