# Generated by Django 3.2.18 on 2023-03-17 17:25

from django.db import migrations
from nautobot.core.models.fields import slugify_dashes_to_underscores
from nautobot.extras.utils import FeatureQuery

CF_KEY_TO_NAME = {}


def generate_unique_custom_field_slug_and_migrate_custom_field_data(apps, schema_editor):
    CustomField = apps.get_model("extras", "customfield")
    ContentType = apps.get_model("contenttypes", "ContentType")

    # Make sure that customfield keys are unique by appending counters
    # and log messages if the old keys are changed.
    cf_keys = set()
    for custom_field in CustomField.objects.all().order_by("created"):
        original_cf_key = custom_field.key
        cf_key = slugify_dashes_to_underscores(original_cf_key)
        append_counter = 2
        while cf_key in cf_keys:
            cf_key_append = f"_{append_counter}"
            max_key_length = 50 - len(cf_key_append)
            cf_key = original_cf_key[:max_key_length] + cf_key_append
            append_counter += 1
        if cf_key != original_cf_key:
            print(
                f'  CustomField instance "{custom_field.label}" key attribute "{original_cf_key}" is being changed to "{cf_key}".'
            )
            custom_field.key = cf_key
            custom_field.save()
        cf_keys.add(cf_key)
        CF_KEY_TO_NAME[custom_field.key] = custom_field.name

    # Move name to labels
    # Filtering on null or empty labels
    custom_fields = CustomField.objects.filter(label__isnull=True).union(CustomField.objects.filter(label__exact=""))

    for cf in custom_fields:
        cf.label = cf.name
        cf.save()

    for ct in ContentType.objects.filter(FeatureQuery("custom_fields").get_query()):
        relevant_custom_fields = CustomField.objects.filter(content_types=ct)
        if not relevant_custom_fields.exists():
            continue
        model = apps.get_model(ct.app_label, ct.model)
        cf_list = []
        for instance in model.objects.all():
            new_custom_field_data = {}
            for cf in relevant_custom_fields:
                new_custom_field_data[cf.key] = instance._custom_field_data.pop(CF_KEY_TO_NAME.get(cf.key), None)
            instance._custom_field_data = new_custom_field_data
            cf_list.append(instance)
        model.objects.bulk_update(cf_list, ["_custom_field_data"], 1000)


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0076_rename_slug_to_key_for_custom_field"),
    ]

    operations = [
        migrations.RunPython(
            code=generate_unique_custom_field_slug_and_migrate_custom_field_data,
            reverse_code=migrations.operations.special.RunPython.noop,
        )
    ]
