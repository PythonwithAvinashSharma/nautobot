# Generated by Django 2.2.8 on 2020-01-15 21:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0035_deterministic_ordering'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfield',
            name='obj_type',
            field=models.ManyToManyField(limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'circuits'), ('model__in', ['circuit', 'provider'])), models.Q(('app_label', 'dcim'), ('model__in', ['device', 'devicetype', 'powerfeed', 'rack', 'site'])), models.Q(('app_label', 'ipam'), ('model__in', ['aggregate', 'ipaddress', 'prefix', 'service', 'vlan', 'vrf'])), models.Q(('app_label', 'secrets'), ('model__in', ['secret'])), models.Q(('app_label', 'tenancy'), ('model__in', ['tenant'])), models.Q(('app_label', 'virtualization'), ('model__in', ['cluster', 'virtualmachine'])), _connector='OR')), related_name='custom_fields', to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='customlink',
            name='content_type',
            field=models.ForeignKey(limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'circuits'), ('model__in', ['circuit', 'provider'])), models.Q(('app_label', 'dcim'), ('model__in', ['cable', 'device', 'devicetype', 'powerpanel', 'powerfeed', 'rack', 'site'])), models.Q(('app_label', 'ipam'), ('model__in', ['aggregate', 'ipaddress', 'prefix', 'service', 'vlan', 'vrf'])), models.Q(('app_label', 'secrets'), ('model__in', ['secret'])), models.Q(('app_label', 'tenancy'), ('model__in', ['tenant'])), models.Q(('app_label', 'virtualization'), ('model__in', ['cluster', 'virtualmachine'])), _connector='OR')), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='exporttemplate',
            name='content_type',
            field=models.ForeignKey(limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'circuits'), ('model__in', ['circuit', 'provider'])), models.Q(('app_label', 'dcim'), ('model__in', ['cable', 'consoleport', 'device', 'devicetype', 'interface', 'inventoryitem', 'manufacturer', 'powerpanel', 'powerport', 'powerfeed', 'rack', 'rackgroup', 'region', 'site', 'virtualchassis'])), models.Q(('app_label', 'ipam'), ('model__in', ['aggregate', 'ipaddress', 'prefix', 'service', 'vlan', 'vrf'])), models.Q(('app_label', 'secrets'), ('model__in', ['secret'])), models.Q(('app_label', 'tenancy'), ('model__in', ['tenant'])), models.Q(('app_label', 'virtualization'), ('model__in', ['cluster', 'virtualmachine'])), _connector='OR')), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='graph',
            name='type',
            field=models.ForeignKey(limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'circuits'), ('model__in', ['provider'])), models.Q(('app_label', 'dcim'), ('model__in', ['device', 'interface', 'site'])), _connector='OR')), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
    ]
