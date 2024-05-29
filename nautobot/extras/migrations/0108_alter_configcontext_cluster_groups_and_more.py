# Generated by Django 4.2.9 on 2024-01-17 18:52

from django.db import migrations, models
import django.db.models.deletion

import nautobot.extras.models.models
import nautobot.extras.models.roles
import nautobot.extras.models.statuses


class Migration(migrations.Migration):
    dependencies = [
        ("dcim", "0060_alter_cable_status_alter_consoleport__path_and_more"),
        ("virtualization", "0026_change_virtualmachine_primary_ip_fields"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("tenancy", "0008_tagsfield"),
        ("extras", "0107_staticgroup_staticgroupassociation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="configcontext",
            name="cluster_groups",
            field=models.ManyToManyField(blank=True, related_name="+", to="virtualization.clustergroup"),
        ),
        migrations.AlterField(
            model_name="configcontext",
            name="clusters",
            field=models.ManyToManyField(blank=True, related_name="+", to="virtualization.cluster"),
        ),
        migrations.AlterField(
            model_name="configcontext",
            name="device_redundancy_groups",
            field=models.ManyToManyField(blank=True, related_name="+", to="dcim.deviceredundancygroup"),
        ),
        migrations.AlterField(
            model_name="configcontext",
            name="device_types",
            field=models.ManyToManyField(blank=True, related_name="+", to="dcim.devicetype"),
        ),
        migrations.AlterField(
            model_name="configcontext",
            name="dynamic_groups",
            field=models.ManyToManyField(
                blank=True,
                limit_choices_to=nautobot.extras.models.models.limit_dynamic_group_choices,
                related_name="+",
                to="extras.dynamicgroup",
            ),
        ),
        migrations.AlterField(
            model_name="configcontext",
            name="locations",
            field=models.ManyToManyField(blank=True, related_name="+", to="dcim.location"),
        ),
        migrations.AlterField(
            model_name="configcontext",
            name="platforms",
            field=models.ManyToManyField(blank=True, related_name="+", to="dcim.platform"),
        ),
        migrations.AlterField(
            model_name="configcontext",
            name="roles",
            field=models.ManyToManyField(blank=True, related_name="+", to="extras.role"),
        ),
        migrations.AlterField(
            model_name="configcontext",
            name="tags",
            field=models.ManyToManyField(blank=True, related_name="+", to="extras.tag"),
        ),
        migrations.AlterField(
            model_name="configcontext",
            name="tenant_groups",
            field=models.ManyToManyField(blank=True, related_name="+", to="tenancy.tenantgroup"),
        ),
        migrations.AlterField(
            model_name="configcontext",
            name="tenants",
            field=models.ManyToManyField(blank=True, related_name="+", to="tenancy.tenant"),
        ),
        migrations.AlterField(
            model_name="contactassociation",
            name="role",
            field=nautobot.extras.models.roles.RoleField(on_delete=django.db.models.deletion.PROTECT, to="extras.role"),
        ),
        migrations.AlterField(
            model_name="contactassociation",
            name="status",
            field=nautobot.extras.models.statuses.StatusField(
                on_delete=django.db.models.deletion.PROTECT, to="extras.status"
            ),
        ),
        migrations.AlterField(
            model_name="taggeditem",
            name="content_type",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_%(class)s_tagged_items",
                to="contenttypes.contenttype",
            ),
        ),
        migrations.AlterField(
            model_name="taggeditem",
            name="tag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_%(class)s_items",
                to="extras.tag",
            ),
        ),
    ]
