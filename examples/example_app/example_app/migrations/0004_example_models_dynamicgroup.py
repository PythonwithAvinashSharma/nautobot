# Generated by Django 3.2.12 on 2022-03-18 22:22

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("example_app", "0003_anotherexamplemodel__custom_field_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="anotherexamplemodel",
            name="created",
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="anotherexamplemodel",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name="examplemodel",
            name="_custom_field_data",
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name="examplemodel",
            name="created",
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="examplemodel",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
