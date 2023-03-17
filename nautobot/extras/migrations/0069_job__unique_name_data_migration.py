# Generated by Django 3.2.18 on 2023-03-15 17:19

from django.db import migrations
from django.template.defaultfilters import slugify

from nautobot.extras.constants import JOB_MAX_NAME_LENGTH


def generate_unique_job_names_and_update_slug(apps, schema_editor):
    """
    Make duplicate Job names unique by appending an incrementing counter to the end.
    Also update slugs to be generated from the Job.name field.
    """
    Job = apps.get_model("extras", "Job")
    job_names = []
    for job_model in Job.objects.all().order_by("created"):
        original_job_name = job_model.name
        job_name = original_job_name
        append_counter = 2
        while job_name in job_names:
            job_name_append = f" ({append_counter})"
            max_name_length = JOB_MAX_NAME_LENGTH - len(job_name_append)
            job_name = original_job_name[:max_name_length] + job_name_append
            append_counter += 1
        if job_name != original_job_name:
            print(
                f'  Job class "{job_model.job_class_name}" name "{original_job_name}" is not unique, changing to "{job_name}".'
            )
            job_model.name = job_name
            job_model.name_override = True
        job_model.slug = slugify(job_name)[:JOB_MAX_NAME_LENGTH]
        job_model.save()
        job_names.append(job_name)


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0068_rename_model_fields"),
    ]

    operations = [
        migrations.RunPython(
            code=generate_unique_job_names_and_update_slug,
            reverse_code=migrations.operations.special.RunPython.noop,
        ),
    ]
