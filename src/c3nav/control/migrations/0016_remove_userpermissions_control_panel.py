# Generated by Django 5.0.8 on 2024-12-12 22:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0015_userpermissions_view_users_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userpermissions',
            name='control_panel',
        ),
    ]
