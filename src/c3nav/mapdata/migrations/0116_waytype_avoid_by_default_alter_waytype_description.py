# Generated by Django 5.0.8 on 2024-12-15 18:23

import c3nav.mapdata.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0115_dataoverlay_access_restriction'),
    ]

    operations = [
        migrations.AddField(
            model_name='waytype',
            name='avoid_by_default',
            field=models.BooleanField(default=False, verbose_name='avoid by default'),
        ),
        migrations.AlterField(
            model_name='waytype',
            name='description',
            field=c3nav.mapdata.fields.I18nField(fallback_any=True, verbose_name='description (downwards or general)'),
        ),
    ]
