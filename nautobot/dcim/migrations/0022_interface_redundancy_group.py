# Generated by Django 3.2.20 on 2023-08-01 17:19

import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import nautobot.core.models.fields
import nautobot.extras.models.mixins
import nautobot.extras.models.statuses
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("ipam", "0009_alter_vlan_name"),
        ("extras", "0058_jobresult_add_time_status_idxs"),
        ("dcim", "0021_platform_network_driver"),
    ]

    operations = [
        migrations.CreateModel(
            name="InterfaceRedundancyGroup",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("protocol", models.CharField(blank=True, max_length=50)),
                ("protocol_group_id", models.CharField(blank=True, max_length=50)),
            ],
            options={
                "ordering": ["name"],
            },
            bases=(
                models.Model,
                nautobot.extras.models.mixins.DynamicGroupMixin,
                nautobot.extras.models.mixins.NotesMixin,
            ),
        ),
        migrations.CreateModel(
            name="InterfaceRedundancyGroupAssociation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                ("priority", models.PositiveSmallIntegerField()),
                (
                    "interface",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="interface_redundancy_group_associations",
                        to="dcim.interface",
                    ),
                ),
                (
                    "interface_redundancy_group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="interface_redundancy_group_associations",
                        to="dcim.interfaceredundancygroup",
                    ),
                ),
            ],
            options={
                "ordering": ("interface_redundancy_group", "-priority"),
                "unique_together": {("interface_redundancy_group", "interface")},
            },
        ),
        migrations.AddField(
            model_name="interfaceredundancygroup",
            name="interfaces",
            field=models.ManyToManyField(
                blank=True,
                related_name="interface_redundancy_groups",
                through="dcim.InterfaceRedundancyGroupAssociation",
                to="dcim.Interface",
            ),
        ),
        migrations.AddField(
            model_name="interfaceredundancygroup",
            name="secrets_group",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="extras.secretsgroup",
            ),
        ),
        migrations.AddField(
            model_name="interfaceredundancygroup",
            name="status",
            field=nautobot.extras.models.statuses.StatusField(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="interface_redundancy_groups",
                to="extras.status",
            ),
        ),
        migrations.AddField(
            model_name="interfaceredundancygroup",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
        migrations.AddField(
            model_name="interfaceredundancygroup",
            name="virtual_ip",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="interface_redundancy_groups",
                to="ipam.ipaddress",
            ),
        ),
    ]
