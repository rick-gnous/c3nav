# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-07-08 12:52
from __future__ import unicode_literals

import os

from django.conf import settings
from django.db import migrations


def move_sources(apps, schema_editor):
    Source = apps.get_model('mapdata', 'Source')
    for source in Source.objects.all():
        with open(settings.SOURCES_ROOT / source.name), 'wb') as f:
            f.write(source.image)


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0015_auto_20170706_1334'),
    ]

    operations = [
        migrations.RunPython(move_sources),
        migrations.RemoveField(
            model_name='source',
            name='image',
        ),
    ]
