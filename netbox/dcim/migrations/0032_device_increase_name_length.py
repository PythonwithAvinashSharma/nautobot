# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-02 15:09
from __future__ import unicode_literals

from django.db import migrations
import utilities.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0031_regions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='name',
            field=utilities.fields.NullableCharField(blank=True, max_length=64, null=True, unique=True),
        ),
    ]
