# Generated by Django 4.2.16 on 2024-12-24 12:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0116_fix_dynamic_group_group_type_data_migration'),
        ('dcim', '0062_module_data_migration'),
        ('naas', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='siteonboarding',
            old_name='num_devices',
            new_name='device_number',
        ),
        migrations.RenameField(
            model_name='siteonboarding',
            old_name='site_name',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='siteonboarding',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='siteonboarding',
            name='num_prefixes',
        ),
        migrations.RemoveField(
            model_name='siteonboarding',
            name='num_vlans',
        ),
        migrations.RemoveField(
            model_name='siteonboarding',
            name='vlan_requirement',
        ),
        migrations.AddField(
            model_name='siteonboarding',
            name='num_prefixes_masks',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='siteonboarding',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='site_onboardings', to='dcim.devicetype'),
        ),
        migrations.AlterField(
            model_name='siteonboarding',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sites', to='dcim.location'),
        ),
        migrations.RemoveField(
            model_name='siteonboarding',
            name='tags',
        ),
        migrations.AddField(
            model_name='siteonboarding',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='+', to='extras.tag'),
        ),
    ]
