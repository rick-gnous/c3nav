# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-10 16:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0075_auto_20170510_1557'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='area',
            name='id',
        ),
        migrations.RemoveField(
            model_name='point',
            name='id',
        ),
        migrations.RemoveField(
            model_name='section',
            name='id',
        ),
        migrations.RemoveField(
            model_name='space',
            name='id',
        ),
        migrations.AlterField(
            model_name='area',
            name='locationslug_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='areas', serialize=False, to='mapdata.LocationSlug'),
        ),
        migrations.AlterField(
            model_name='locationgroup',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='locationgroup',
            name='locationslug_ptr',
            field=models.OneToOneField(db_column='locationslug_ptr', on_delete=django.db.models.deletion.CASCADE, related_name='locationgroups', to='mapdata.LocationSlug'),
        ),
        migrations.AlterField(
            model_name='point',
            name='locationslug_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='points', serialize=False, to='mapdata.LocationSlug'),
        ),
        migrations.AlterField(
            model_name='section',
            name='locationslug_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='sections', serialize=False, to='mapdata.LocationSlug'),
        ),
        migrations.AlterField(
            model_name='space',
            name='locationslug_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='spaces', serialize=False, to='mapdata.LocationSlug'),
        ),
    ]
