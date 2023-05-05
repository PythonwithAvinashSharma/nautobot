# Generated by Django 3.2.18 on 2023-04-21 13:59

from django.db import migrations
import nautobot.core.models.fields


class Migration(migrations.Migration):
    dependencies = [
        ("extras", "0079_tagsfield"),
        ("tenancy", "0007_remove_tenant_tenantgroup_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="tenant",
            name="tags",
            field=nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag"),
        ),
    ]
