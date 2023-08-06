# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_super_cms', '0003_auto_20150326_0741'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(null=True, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='category name')),
                ('description', models.CharField(max_length=255, null=True, verbose_name='category description', blank=True)),
                ('order', models.IntegerField(default=0, verbose_name='order')),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='django_super_cms.Category', null=True)),
            ],
            options={
                'ordering': ['-created_at', 'order'],
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(null=True, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='tag name')),
                ('description', models.CharField(max_length=255, null=True, verbose_name='tag description', blank=True)),
                ('posts', models.ManyToManyField(related_name='tags', null=True, to='django_super_cms.Post', blank=True)),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='post',
            name='category',
            field=models.ForeignKey(related_name='posts', blank=True, to='django_super_cms.Category', null=True),
            preserve_default=True,
        ),
    ]
