# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('django_super_cms', '0004_auto_20150326_0800'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='avatar',
            field=sorl.thumbnail.fields.ImageField(upload_to=b'account/avatar/%Y/%m/%d', null=True, verbose_name='user avatar', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='display_name',
            field=models.CharField(unique=True, max_length=25, verbose_name='user display name'),
            preserve_default=True,
        ),
    ]
