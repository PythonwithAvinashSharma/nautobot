# Generated by Django 3.2.18 on 2023-05-09 16:38

from django.db import migrations
from nautobot.core.models.fields import slugify_dashes_to_underscores


def ensure_relationship_keys_are_unique(apps, schema_editor):
    Relationship = apps.get_model("extras", "relationship")

    relationship_keys = []

    for rel in Relationship.objects.all().order_by("created"):
        original_rel_key = rel.key
        rel_key = slugify_dashes_to_underscores(original_rel_key)
        append_counter = 2

        while rel_key in relationship_keys:
            rel_key_append = f"_{append_counter}"
            max_key_length = 50 - len(rel_key_append)
            rel_key = original_rel_key[:max_key_length] + rel_key_append
            append_counter += 1

        if rel_key != original_rel_key:
            print(
                f'  Relationship instance "{rel.name}" key attribute "{original_rel_key}" is being changed to "{rel_key}".'
            )
            rel.key = rel_key
            rel.save()


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0081_rename_relationship_name_to_label"),
    ]

    operations = [
        migrations.RunPython(
            code=ensure_relationship_keys_are_unique,
            reverse_code=migrations.operations.special.RunPython.noop,
        )
    ]
