# Generated by Django 3.2.14 on 2022-07-21 18:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0039_jobresult_job_kwargs"),
    ]

    operations = [
        migrations.AddField(
            model_name="job",
            name="is_job_hook_receiver",
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
