# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-10 16:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0077_auto_20170510_1637'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LocationGroup',
            new_name='LegacyLocationGroup',
        ),
    ]
