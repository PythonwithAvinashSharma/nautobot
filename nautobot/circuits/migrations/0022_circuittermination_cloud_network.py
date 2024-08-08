# Generated by Django 4.2.14 on 2024-07-18 16:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("cloud", "0001_initial"),
        ("circuits", "0021_alter_circuit_status_alter_circuittermination__path"),
    ]

    operations = [
        migrations.AddField(
            model_name="circuittermination",
            name="cloud_network",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="circuit_terminations",
                to="cloud.cloudnetwork",
            ),
        ),
    ]
