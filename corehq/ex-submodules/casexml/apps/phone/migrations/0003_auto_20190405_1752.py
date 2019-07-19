# -*- coding: utf-8 -*-
# flake8: noqa
# Generated by Django 1.11.20 on 2019-04-05 17:52
from __future__ import absolute_import
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('phone', '0002_synclogsql'),
    ]

    operations = [
        migrations.AlterField(
            model_name='synclogsql',
            name='synclog_id',
            field=models.UUIDField(default=uuid.uuid1, primary_key=True, serialize=False, unique=True),
        ),
    ]
