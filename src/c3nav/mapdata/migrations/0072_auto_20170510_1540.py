# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-05-10 15:40
from __future__ import unicode_literals

from django.db import migrations, models


def create_locationslugs(apps, schema_editor):
    LocationSlug = apps.get_model('mapdata', 'LocationSlug')
    for model in ('Section', 'Space', 'Area', 'Point', 'LocationGroup'):
        Model = apps.get_model('mapdata', model)
        for obj in Model.objects.all():
            slug = LocationSlug.objects.create(slug=getattr(obj, 'slug', None))
            obj.slug_ptr = slug
            obj.save()


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0071_auto_20170510_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationslug',
            name='slug',
            field=models.SlugField(null=True, unique=True, verbose_name='name'),
        ),
        migrations.RunPython(create_locationslugs),
    ]
