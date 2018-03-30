# Generated by Django 2.0.3 on 2018-03-30 14:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0055_virtualchassis_ordering'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='untagged_vlan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interfaces_as_untagged', to='ipam.VLAN', verbose_name='Untagged VLAN'),
        ),
        migrations.AlterField(
            model_name='platform',
            name='manufacturer',
            field=models.ForeignKey(blank=True, help_text='Optionally limit this platform to devices of a certain manufacturer', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='platforms', to='dcim.Manufacturer'),
        ),
    ]
