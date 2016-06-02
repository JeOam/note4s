# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-29 12:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20160529_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subnote',
            name='note',
            field=models.ForeignKey(db_column='note_uuid', on_delete=django.db.models.deletion.CASCADE, related_name='sub_notes', to='api.Note'),
        ),
    ]