# Generated by Django 3.2.16 on 2023-01-11 00:53

from django.db import migrations
import nautobot.utilities.tree_queries


class Migration(migrations.Migration):

    dependencies = [
        ("dcim", "0027_remove_device_role_and_rack_role"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="inventoryitem",
            managers=[
                ("objects", nautobot.utilities.tree_queries.TreeManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name="locationtype",
            managers=[
                ("objects", nautobot.utilities.tree_queries.TreeManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name="rackgroup",
            managers=[
                ("objects", nautobot.utilities.tree_queries.TreeManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name="region",
            managers=[
                ("objects", nautobot.utilities.tree_queries.TreeManager()),
            ],
        ),
    ]
