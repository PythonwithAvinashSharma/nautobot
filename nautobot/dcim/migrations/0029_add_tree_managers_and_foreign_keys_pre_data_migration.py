# Generated by Django 3.2.16 on 2023-01-23 22:45

from django.db import migrations, models
import django.db.models.deletion
import nautobot.core.models.tree_queries


class Migration(migrations.Migration):

    dependencies = [
        ("circuits", "0009_circuittermination_location"),
        ("dcim", "0028_rename_foreignkey_fields"),
        ("ipam", "0015_prefix_add_type"),
        ("virtualization", "0015_rename_foreignkey_fields"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="inventoryitem",
            managers=[
                ("objects", nautobot.core.models.tree_queries.TreeManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name="locationtype",
            managers=[
                ("objects", nautobot.core.models.tree_queries.TreeManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name="rackgroup",
            managers=[
                ("objects", nautobot.core.models.tree_queries.TreeManager()),
            ],
        ),
        migrations.AlterModelManagers(
            name="region",
            managers=[
                ("objects", nautobot.core.models.tree_queries.TreeManager()),
            ],
        ),
        migrations.AddField(
            model_name="region",
            name="migrated_location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="regions",
                to="dcim.location",
            ),
        ),
        migrations.AddField(
            model_name="site",
            name="migrated_location",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sites",
                to="dcim.location",
            ),
        ),
    ]
