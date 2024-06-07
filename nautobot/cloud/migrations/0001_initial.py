# Generated by Django 4.2.13 on 2024-06-05 18:19

import uuid

import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion

import nautobot.core.models.fields
import nautobot.extras.models.mixins


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("dcim", "0062_module_data_migration"),
        ("ipam", "0047_alter_ipaddress_role_alter_ipaddress_status_and_more"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("extras", "0108_alter_configcontext_cluster_groups_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CloudAccount",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("account_number", models.CharField(max_length=255)),
                (
                    "provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cloud_accounts",
                        to="dcim.manufacturer",
                    ),
                ),
                (
                    "secrets_group",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="extras.secretsgroup",
                    ),
                ),
                ("tags", nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "ordering": ["name"],
            },
            bases=(
                nautobot.extras.models.mixins.DynamicGroupMixin,
                nautobot.extras.models.mixins.NotesMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="CloudNetwork",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("extra_config", models.JSONField(blank=True, null=True)),
                (
                    "cloud_account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="cloud_networks",
                        to="cloud.cloudaccount",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
            bases=(
                nautobot.extras.models.mixins.DynamicGroupMixin,
                nautobot.extras.models.mixins.NotesMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="CloudType",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
                ("description", models.CharField(blank=True, max_length=255)),
                ("config_schema", models.JSONField(blank=True, null=True)),
                (
                    "content_types",
                    models.ManyToManyField(
                        limit_choices_to=models.Q(("app_label", "cloud"), ("model", "cloudnetwork")),
                        related_name="cloud_types",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "provider",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="cloud_types", to="dcim.manufacturer"
                    ),
                ),
                ("tags", nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag")),
            ],
            options={
                "ordering": ["name"],
            },
            bases=(
                nautobot.extras.models.mixins.DynamicGroupMixin,
                nautobot.extras.models.mixins.NotesMixin,
                models.Model,
            ),
        ),
        migrations.CreateModel(
            name="CloudNetworkPrefixAssignment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                (
                    "cloud_network",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prefix_assignments",
                        to="cloud.cloudnetwork",
                    ),
                ),
                (
                    "prefix",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cloud_network_assignments",
                        to="ipam.prefix",
                    ),
                ),
            ],
            options={
                "ordering": ["cloud_network", "prefix"],
                "unique_together": {("cloud_network", "prefix")},
            },
        ),
        migrations.AddField(
            model_name="cloudnetwork",
            name="cloud_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, related_name="cloud_networks", to="cloud.cloudtype"
            ),
        ),
        migrations.AddField(
            model_name="cloudnetwork",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                to="cloud.cloudnetwork",
            ),
        ),
        migrations.AddField(
            model_name="cloudnetwork",
            name="prefixes",
            field=models.ManyToManyField(
                blank=True,
                related_name="cloud_networks",
                through="cloud.CloudNetworkPrefixAssignment",
                to="ipam.prefix",
            ),
        ),
        migrations.AddField(
            model_name="cloudnetwork",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
    ]
