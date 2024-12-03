# Generated by Django 3.1.3 on 2020-12-28 21:26

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("example_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AnotherExampleModel",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=20)),
                ("number", models.IntegerField(default=100)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]
