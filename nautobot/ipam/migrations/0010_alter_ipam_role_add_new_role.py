# Generated by Django 3.2.16 on 2022-11-23 12:27

from django.db import migrations
import django.db.models.deletion
import nautobot.extras.models.roles


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0059_collect_roles_from_related_apps_roles"),
        ("ipam", "0009_alter_vlan_name"),
    ]

    operations = [
        ####################
        # Prefix
        ####################
        migrations.RenameField(
            model_name="prefix",
            old_name="role",
            new_name="legacy_role",
        ),
        migrations.AddField(
            model_name="prefix",
            name="new_role",
            field=nautobot.extras.models.roles.RoleField(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ipam_prefix_related",
                to="extras.role",
            ),
        ),
        ####################
        # VLAN
        ####################
        migrations.RenameField(
            model_name="vlan",
            old_name="role",
            new_name="legacy_role",
        ),
        migrations.AddField(
            model_name="vlan",
            name="new_role",
            field=nautobot.extras.models.roles.RoleField(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ipam_vlan_related",
                to="extras.role",
            ),
        ),
        ####################
        # IPAddress
        ####################
        migrations.RenameField(
            model_name="ipaddress",
            old_name="role",
            new_name="legacy_role",
        ),
        migrations.AddField(
            model_name="ipaddress",
            name="new_role",
            field=nautobot.extras.models.roles.RoleField(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ipam_ipaddress_related",
                to="extras.role",
            ),
        ),
    ]
