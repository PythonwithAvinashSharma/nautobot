# Generated by Django 3.2.18 on 2023-06-12 22:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("circuits", "0018_status_nonnullable"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="providernetwork",
            name="slug",
        ),
    ]
