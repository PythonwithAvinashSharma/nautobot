# Generated by Django 3.2.23 on 2024-01-03 17:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0052_fix_interface_redundancy_group_created"),
        ("ipam", "0039_alter_ipaddresstointerface_ip_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="vlan",
            name="locations",
            field=models.ManyToManyField(blank=True, related_name="vlans", to="dcim.Location"),
        ),
    ]
