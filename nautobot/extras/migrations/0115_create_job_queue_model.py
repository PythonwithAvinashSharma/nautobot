# Generated by Django 4.2.15 on 2024-08-13 20:36

import uuid

import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion

import nautobot.core.models.fields
import nautobot.extras.models.mixins


class Migration(migrations.Migration):
    dependencies = [
        ("tenancy", "0009_update_all_charfields_max_length_to_255"),
        ("extras", "0114_computedfield_grouping"),
    ]

    operations = [
        migrations.CreateModel(
            name="JobQueue",
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
                ("queue_type", models.CharField(max_length=50)),
                ("tags", nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag")),
                (
                    "tenant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="job_queues",
                        to="tenancy.tenant",
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
            name="JobQueueAssignment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job_queue_assignments",
                        to="extras.job",
                    ),
                ),
                (
                    "job_queue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job_assignments",
                        to="extras.jobqueue",
                    ),
                ),
            ],
            options={
                "ordering": ["job", "job_queue"],
                "unique_together": {("job", "job_queue")},
            },
        ),
        migrations.AddField(
            model_name="job",
            name="job_queues",
            field=models.ManyToManyField(
                related_name="jobs", through="extras.JobQueueAssignment", to="extras.jobqueue"
            ),
        ),
    ]
