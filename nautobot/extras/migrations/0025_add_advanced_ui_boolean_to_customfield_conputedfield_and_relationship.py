# Generated by Django 3.1.14 on 2022-03-03 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0024_job_data_migration"),
    ]

    operations = [
        migrations.AddField(
            model_name="computedfield",
            name="advanced_ui",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="customfield",
            name="advanced_ui",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="relationship",
            name="advanced_ui",
            field=models.BooleanField(default=False),
        ),
    ]
