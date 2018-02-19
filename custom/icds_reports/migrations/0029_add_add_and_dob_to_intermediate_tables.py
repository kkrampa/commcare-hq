# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-04 15:05
from __future__ import unicode_literals

from __future__ import absolute_import
from django.db import migrations

from corehq.sql_db.operations import RawSQLMigration

migrator = RawSQLMigration(('custom', 'icds_reports', 'migrations', 'sql_templates'))


class Migration(migrations.Migration):

    dependencies = [
        ('icds_reports', '0028_auto_20171204_1922'),
    ]

    operations = [
        migrator.get_migration('update_tables12.sql'),
    ]
