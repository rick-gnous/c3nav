# Generated by Django 5.0.8 on 2024-12-28 13:26

from django.db import migrations, models


def add_beacon_type(apps, schema_editor):
    RangingBeacon = apps.get_model('mapdata', 'rangingbeacon')
    RangingBeacon.objects.filter(import_tag__startswith='noc:').update(beacon_type="event_wifi")


class Migration(migrations.Migration):

    dependencies = [
        ('mapdata', '0134_rangingbeacon_ap_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='rangingbeacon',
            name='beacon_type',
            field=models.CharField(blank=True, choices=[('event_wifi', 'Event WiFi AP'), ('dect', 'DECT antenna')], max_length=16, null=True, verbose_name='beacon type'),
        ),
        migrations.RunPython(add_beacon_type, migrations.RunPython.noop),
    ]
