# Generated by Django 2.2 on 2019-04-22 21:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0026_prefix_ordering_vrf_nulls_first'),
    ]

    operations = [
        migrations.AddField(
            model_name='ipaddress',
            name='dns_name',
            field=models.CharField(blank=True, max_length=255, validators=[django.core.validators.RegexValidator(code='invalid', message='Only alphanumeric characters, hyphens, periods, and underscores are allowed in DNS names', regex='^[0-9A-Za-z.-_]+$')]),
        ),
    ]
