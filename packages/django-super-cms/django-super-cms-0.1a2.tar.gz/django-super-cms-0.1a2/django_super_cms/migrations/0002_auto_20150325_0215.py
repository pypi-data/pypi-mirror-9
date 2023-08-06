# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('django_super_cms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(null=True, blank=True)),
                ('author_name', models.CharField(max_length=255, verbose_name='author name')),
                ('author_url', models.CharField(max_length=255, null=True, verbose_name='author url', blank=True)),
                ('content', models.TextField(verbose_name='comment content')),
                ('is_approved', models.BooleanField(default=False, verbose_name='is comment approved')),
                ('author', models.ForeignKey(related_name='comments', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='django_super_cms.Comment', null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'comments',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(null=True, blank=True)),
                ('title', models.CharField(max_length=255, verbose_name='post title')),
                ('content', models.TextField(verbose_name='post content')),
                ('author_name', models.CharField(max_length=255, verbose_name='post author name')),
                ('status', models.IntegerField(default=0, verbose_name='post status', choices=[(0, b'show'), (1, b'hide')])),
                ('slug', models.CharField(max_length=255, verbose_name='post slug')),
                ('click', models.IntegerField(default=0, verbose_name='post click')),
                ('template_name', models.CharField(max_length=255, verbose_name='post templte name')),
                ('post_type', models.IntegerField(default=1, verbose_name='post type', choices=[(0, b'page'), (1, b'post')])),
                ('author', models.ForeignKey(related_name='posts', to=settings.AUTH_USER_MODEL)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='django_super_cms.Post', null=True)),
            ],
            options={
                'ordering': ['-created_at', '-click'],
                'verbose_name': 'post',
                'verbose_name_plural': 'posts',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(related_name='comments', to='django_super_cms.Post'),
            preserve_default=True,
        ),
    ]
