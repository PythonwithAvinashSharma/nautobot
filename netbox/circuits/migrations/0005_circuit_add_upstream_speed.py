# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-08 20:24
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0004_circuit_add_tenant'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuit',
            name='upstream_speed',
            field=models.PositiveIntegerField(blank=True, help_text=b'Upstream speed, if different from port speed', null=True, verbose_name=b'Upstream speed (Kbps)'),
        ),
    ]
