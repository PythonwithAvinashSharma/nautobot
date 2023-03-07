# Generated by Django 3.2.17 on 2023-02-21 21:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("circuits", "0011_remove_site_foreign_key_from_circuit_termination_class"),
        ("dcim", "0035_related_name_changes"),
        ("django_celery_results", "0006_taskresult_date_created"),
        ("extras", "0065_remove_site_and_region_attributes_from_config_context"),
        ("ipam", "0018_remove_site_foreign_key_from_ipam_models"),
        ("virtualization", "0016_remove_site_foreign_key_from_cluster_class"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="site",
            name="region",
        ),
        migrations.RemoveField(
            model_name="site",
            name="status",
        ),
        migrations.RemoveField(
            model_name="site",
            name="tags",
        ),
        migrations.RemoveField(
            model_name="site",
            name="tenant",
        ),
        migrations.DeleteModel(
            name="Region",
        ),
        migrations.DeleteModel(
            name="Site",
        ),
    ]
