# Generated by Django 3.1.7 on 2021-04-01 06:35

import django.core.serializers.json
from django.db import migrations, models
import nautobot.dcim.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Circuit",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("cid", models.CharField(max_length=100)),
                ("install_date", models.DateField(blank=True, null=True)),
                ("commit_rate", models.PositiveIntegerField(blank=True, null=True)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("comments", models.TextField(blank=True)),
            ],
            options={
                "ordering": ["provider", "cid"],
            },
        ),
        migrations.CreateModel(
            name="CircuitTermination",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("_cable_peer_id", models.UUIDField(blank=True, null=True)),
                ("term_side", models.CharField(max_length=1)),
                ("port_speed", models.PositiveIntegerField(blank=True, null=True)),
                ("upstream_speed", models.PositiveIntegerField(blank=True, null=True)),
                ("xconnect_id", models.CharField(blank=True, max_length=50)),
                ("pp_info", models.CharField(blank=True, max_length=100)),
                ("description", models.CharField(blank=True, max_length=200)),
            ],
            options={
                "ordering": ["circuit", "term_side"],
            },
        ),
        migrations.CreateModel(
            name="CircuitType",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("description", models.CharField(blank=True, max_length=200)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Provider",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                ("asn", nautobot.dcim.fields.ASNField(blank=True, null=True)),
                ("account", models.CharField(blank=True, max_length=30)),
                ("portal_url", models.URLField(blank=True)),
                ("noc_contact", models.TextField(blank=True)),
                ("admin_contact", models.TextField(blank=True)),
                ("comments", models.TextField(blank=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]
