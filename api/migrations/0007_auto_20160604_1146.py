# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-04 11:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20160529_1257'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notesection',
            name='note_book',
        ),
        migrations.AddField(
            model_name='notesection',
            name='notebook',
            field=models.ForeignKey(db_column='notebook_uuid', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='note_sections', to='api.NoteBook'),
        ),
    ]
