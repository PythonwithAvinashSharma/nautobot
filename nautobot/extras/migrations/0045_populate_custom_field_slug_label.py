# Generated by Django 3.2.14 on 2022-08-01 18:52

from django.db import migrations, models
from nautobot.utilities.utils import slugify_dashes_to_underscores


def populate_custom_field_slugs_labels(apps, schema_editor):
    CustomField = apps.get_model("extras", "CustomField")
    for cf in CustomField.objects.all():
        cf.slug = slugify_dashes_to_underscores(cf.name)
        cf.save()
    CustomField.objects.filter(label="").update(label=models.F("name"))


def clear_custom_field_slugs_labels(apps, schema_editor):
    CustomField = apps.get_model("extras", "CustomField")
    CustomField.objects.all().update(slug="")
    CustomField.objects.filter(label=models.F("name")).update(label="")


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0044_add_custom_field_slug"),
    ]

    operations = [
        migrations.RunPython(populate_custom_field_slugs_labels, reverse_code=clear_custom_field_slugs_labels),
    ]
