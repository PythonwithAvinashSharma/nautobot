import django.contrib.postgres.fields
import django.core.validators
import django.db.models.deletion
import mptt.fields
from django.conf import settings
from django.db import migrations, models

import dcim.fields
import utilities.fields


def copy_site_from_rack(apps, schema_editor):
    Device = apps.get_model('dcim', 'Device')
    for device in Device.objects.all():
        device.site = device.rack.site
        device.save()


def rpc_client_to_napalm_driver(apps, schema_editor):
    """
    Migrate legacy RPC clients to their respective NAPALM drivers
    """
    Platform = apps.get_model('dcim', 'Platform')

    Platform.objects.filter(rpc_client='juniper-junos').update(napalm_driver='junos')
    Platform.objects.filter(rpc_client='cisco-ios').update(napalm_driver='ios')


class Migration(migrations.Migration):

    replaces = [('dcim', '0023_devicetype_comments'), ('dcim', '0024_site_add_contact_fields'), ('dcim', '0025_devicetype_add_interface_ordering'), ('dcim', '0026_add_rack_reservations'), ('dcim', '0027_device_add_site'), ('dcim', '0028_device_copy_rack_to_site'), ('dcim', '0029_allow_rackless_devices'), ('dcim', '0030_interface_add_lag'), ('dcim', '0031_regions'), ('dcim', '0032_device_increase_name_length'), ('dcim', '0033_rackreservation_rack_editable'), ('dcim', '0034_rename_module_to_inventoryitem'), ('dcim', '0035_device_expand_status_choices'), ('dcim', '0036_add_ff_juniper_vcp'), ('dcim', '0037_unicode_literals'), ('dcim', '0038_wireless_interfaces'), ('dcim', '0039_interface_add_enabled_mtu'), ('dcim', '0040_inventoryitem_add_asset_tag_description'), ('dcim', '0041_napalm_integration'), ('dcim', '0042_interface_ff_10ge_cx4'), ('dcim', '0043_device_component_name_lengths')]

    dependencies = [
        ('dcim', '0022_color_names_to_rgb'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='devicetype',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='site',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254, verbose_name=b'Contact E-mail'),
        ),
        migrations.AddField(
            model_name='site',
            name='contact_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='site',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AddField(
            model_name='devicetype',
            name='interface_ordering',
            field=models.PositiveSmallIntegerField(choices=[[1, b'Slot/position'], [2, b'Name (alphabetically)']], default=1),
        ),
        migrations.CreateModel(
            name='RackReservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('units', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveSmallIntegerField(), size=None)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('description', models.CharField(max_length=100)),
                ('rack', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='dcim.Rack')),
                ('user', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.AddField(
            model_name='device',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='devices', to='dcim.Site'),
        ),
        migrations.RunPython(
            code=copy_site_from_rack,
        ),
        migrations.AlterField(
            model_name='device',
            name='rack',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='devices', to='dcim.Rack'),
        ),
        migrations.AlterField(
            model_name='device',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='devices', to='dcim.Site'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[[b'Virtual interfaces', [[0, b'Virtual'], [200, b'Link Aggregation Group (LAG)']]], [b'Ethernet (fixed)', [[800, b'100BASE-TX (10/100ME)'], [1000, b'1000BASE-T (1GE)'], [1150, b'10GBASE-T (10GE)']]], [b'Ethernet (modular)', [[1050, b'GBIC (1GE)'], [1100, b'SFP (1GE)'], [1200, b'SFP+ (10GE)'], [1300, b'XFP (10GE)'], [1310, b'XENPAK (10GE)'], [1320, b'X2 (10GE)'], [1350, b'SFP28 (25GE)'], [1400, b'QSFP+ (40GE)'], [1500, b'CFP (100GE)'], [1600, b'QSFP28 (100GE)']]], [b'FibreChannel', [[3010, b'SFP (1GFC)'], [3020, b'SFP (2GFC)'], [3040, b'SFP (4GFC)'], [3080, b'SFP+ (8GFC)'], [3160, b'SFP+ (16GFC)']]], [b'Serial', [[4000, b'T1 (1.544 Mbps)'], [4010, b'E1 (2.048 Mbps)'], [4040, b'T3 (45 Mbps)'], [4050, b'E3 (34 Mbps)'], [4050, b'E3 (34 Mbps)']]], [b'Stacking', [[5000, b'Cisco StackWise'], [5050, b'Cisco StackWise Plus'], [5100, b'Cisco FlexStack'], [5150, b'Cisco FlexStack Plus']]], [b'Other', [[32767, b'Other']]]], default=1200),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[[b'Virtual interfaces', [[0, b'Virtual'], [200, b'Link Aggregation Group (LAG)']]], [b'Ethernet (fixed)', [[800, b'100BASE-TX (10/100ME)'], [1000, b'1000BASE-T (1GE)'], [1150, b'10GBASE-T (10GE)']]], [b'Ethernet (modular)', [[1050, b'GBIC (1GE)'], [1100, b'SFP (1GE)'], [1200, b'SFP+ (10GE)'], [1300, b'XFP (10GE)'], [1310, b'XENPAK (10GE)'], [1320, b'X2 (10GE)'], [1350, b'SFP28 (25GE)'], [1400, b'QSFP+ (40GE)'], [1500, b'CFP (100GE)'], [1600, b'QSFP28 (100GE)']]], [b'FibreChannel', [[3010, b'SFP (1GFC)'], [3020, b'SFP (2GFC)'], [3040, b'SFP (4GFC)'], [3080, b'SFP+ (8GFC)'], [3160, b'SFP+ (16GFC)']]], [b'Serial', [[4000, b'T1 (1.544 Mbps)'], [4010, b'E1 (2.048 Mbps)'], [4040, b'T3 (45 Mbps)'], [4050, b'E3 (34 Mbps)'], [4050, b'E3 (34 Mbps)']]], [b'Stacking', [[5000, b'Cisco StackWise'], [5050, b'Cisco StackWise Plus'], [5100, b'Cisco FlexStack'], [5150, b'Cisco FlexStack Plus']]], [b'Other', [[32767, b'Other']]]], default=1200),
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='dcim.Region')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='site',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sites', to='dcim.Region'),
        ),
        migrations.AlterField(
            model_name='device',
            name='name',
            field=utilities.fields.NullableCharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='rackreservation',
            name='rack',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservations', to='dcim.Rack'),
        ),
        migrations.RenameModel(
            old_name='Module',
            new_name='InventoryItem',
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='device',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory_items', to='dcim.Device'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_items', to='dcim.InventoryItem'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='manufacturer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inventory_items', to='dcim.Manufacturer'),
        ),
        migrations.AlterField(
            model_name='device',
            name='status',
            field=models.PositiveIntegerField(choices=[[1, b'Active'], [0, b'Offline'], [2, b'Planned'], [3, b'Staged'], [4, b'Failed'], [5, b'Inventory']], default=1, verbose_name=b'Status'),
        ),
        migrations.AlterField(
            model_name='device',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[[1, b'Active'], [0, b'Offline'], [2, b'Planned'], [3, b'Staged'], [4, b'Failed'], [5, b'Inventory']], default=1, verbose_name=b'Status'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[[b'Virtual interfaces', [[0, b'Virtual'], [200, b'Link Aggregation Group (LAG)']]], [b'Ethernet (fixed)', [[800, b'100BASE-TX (10/100ME)'], [1000, b'1000BASE-T (1GE)'], [1150, b'10GBASE-T (10GE)']]], [b'Ethernet (modular)', [[1050, b'GBIC (1GE)'], [1100, b'SFP (1GE)'], [1200, b'SFP+ (10GE)'], [1300, b'XFP (10GE)'], [1310, b'XENPAK (10GE)'], [1320, b'X2 (10GE)'], [1350, b'SFP28 (25GE)'], [1400, b'QSFP+ (40GE)'], [1500, b'CFP (100GE)'], [1600, b'QSFP28 (100GE)']]], [b'FibreChannel', [[3010, b'SFP (1GFC)'], [3020, b'SFP (2GFC)'], [3040, b'SFP (4GFC)'], [3080, b'SFP+ (8GFC)'], [3160, b'SFP+ (16GFC)']]], [b'Serial', [[4000, b'T1 (1.544 Mbps)'], [4010, b'E1 (2.048 Mbps)'], [4040, b'T3 (45 Mbps)'], [4050, b'E3 (34 Mbps)'], [4050, b'E3 (34 Mbps)']]], [b'Stacking', [[5000, b'Cisco StackWise'], [5050, b'Cisco StackWise Plus'], [5100, b'Cisco FlexStack'], [5150, b'Cisco FlexStack Plus'], [5200, b'Juniper VCP']]], [b'Other', [[32767, b'Other']]]], default=1200),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[[b'Virtual interfaces', [[0, b'Virtual'], [200, b'Link Aggregation Group (LAG)']]], [b'Ethernet (fixed)', [[800, b'100BASE-TX (10/100ME)'], [1000, b'1000BASE-T (1GE)'], [1150, b'10GBASE-T (10GE)']]], [b'Ethernet (modular)', [[1050, b'GBIC (1GE)'], [1100, b'SFP (1GE)'], [1200, b'SFP+ (10GE)'], [1300, b'XFP (10GE)'], [1310, b'XENPAK (10GE)'], [1320, b'X2 (10GE)'], [1350, b'SFP28 (25GE)'], [1400, b'QSFP+ (40GE)'], [1500, b'CFP (100GE)'], [1600, b'QSFP28 (100GE)']]], [b'FibreChannel', [[3010, b'SFP (1GFC)'], [3020, b'SFP (2GFC)'], [3040, b'SFP (4GFC)'], [3080, b'SFP+ (8GFC)'], [3160, b'SFP+ (16GFC)']]], [b'Serial', [[4000, b'T1 (1.544 Mbps)'], [4010, b'E1 (2.048 Mbps)'], [4040, b'T3 (45 Mbps)'], [4050, b'E3 (34 Mbps)'], [4050, b'E3 (34 Mbps)']]], [b'Stacking', [[5000, b'Cisco StackWise'], [5050, b'Cisco StackWise Plus'], [5100, b'Cisco FlexStack'], [5150, b'Cisco FlexStack Plus'], [5200, b'Juniper VCP']]], [b'Other', [[32767, b'Other']]]], default=1200),
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='connection_status',
            field=models.NullBooleanField(choices=[[False, 'Planned'], [True, 'Connected']], default=True),
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='cs_port',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='connected_console', to='dcim.ConsoleServerPort', verbose_name='Console server port'),
        ),
        migrations.AlterField(
            model_name='device',
            name='asset_tag',
            field=utilities.fields.NullableCharField(blank=True, help_text='A unique tag used to identify this device', max_length=50, null=True, unique=True, verbose_name='Asset tag'),
        ),
        migrations.AlterField(
            model_name='device',
            name='face',
            field=models.PositiveSmallIntegerField(blank=True, choices=[[0, 'Front'], [1, 'Rear']], null=True, verbose_name='Rack face'),
        ),
        migrations.AlterField(
            model_name='device',
            name='position',
            field=models.PositiveSmallIntegerField(blank=True, help_text='The lowest-numbered unit occupied by the device', null=True, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Position (U)'),
        ),
        migrations.AlterField(
            model_name='device',
            name='primary_ip4',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_ip4_for', to='ipam.IPAddress', verbose_name='Primary IPv4'),
        ),
        migrations.AlterField(
            model_name='device',
            name='primary_ip6',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='primary_ip6_for', to='ipam.IPAddress', verbose_name='Primary IPv6'),
        ),
        migrations.AlterField(
            model_name='device',
            name='serial',
            field=models.CharField(blank=True, max_length=50, verbose_name='Serial number'),
        ),
        migrations.AlterField(
            model_name='device',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[[1, 'Active'], [0, 'Offline'], [2, 'Planned'], [3, 'Staged'], [4, 'Failed'], [5, 'Inventory']], default=1, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='devicebay',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='interface_ordering',
            field=models.PositiveSmallIntegerField(choices=[[1, 'Slot/position'], [2, 'Name (alphabetically)']], default=1),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='is_console_server',
            field=models.BooleanField(default=False, help_text='This type of device has console server ports', verbose_name='Is a console server'),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='is_full_depth',
            field=models.BooleanField(default=True, help_text='Device consumes both front and rear rack faces', verbose_name='Is full depth'),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='is_network_device',
            field=models.BooleanField(default=True, help_text='This type of device has network interfaces', verbose_name='Is a network device'),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='is_pdu',
            field=models.BooleanField(default=False, help_text='This type of device has power outlets', verbose_name='Is a PDU'),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='part_number',
            field=models.CharField(blank=True, help_text='Discrete part number (optional)', max_length=50),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='subdevice_role',
            field=models.NullBooleanField(choices=[(None, 'None'), (True, 'Parent'), (False, 'Child')], default=None, help_text='Parent devices house child devices in device bays. Select "None" if this device type is neither a parent nor a child.', verbose_name='Parent/child status'),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='u_height',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Height (U)'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[['Virtual interfaces', [[0, 'Virtual'], [200, 'Link Aggregation Group (LAG)']]], ['Ethernet (fixed)', [[800, '100BASE-TX (10/100ME)'], [1000, '1000BASE-T (1GE)'], [1150, '10GBASE-T (10GE)']]], ['Ethernet (modular)', [[1050, 'GBIC (1GE)'], [1100, 'SFP (1GE)'], [1200, 'SFP+ (10GE)'], [1300, 'XFP (10GE)'], [1310, 'XENPAK (10GE)'], [1320, 'X2 (10GE)'], [1350, 'SFP28 (25GE)'], [1400, 'QSFP+ (40GE)'], [1500, 'CFP (100GE)'], [1600, 'QSFP28 (100GE)']]], ['FibreChannel', [[3010, 'SFP (1GFC)'], [3020, 'SFP (2GFC)'], [3040, 'SFP (4GFC)'], [3080, 'SFP+ (8GFC)'], [3160, 'SFP+ (16GFC)']]], ['Serial', [[4000, 'T1 (1.544 Mbps)'], [4010, 'E1 (2.048 Mbps)'], [4040, 'T3 (45 Mbps)'], [4050, 'E3 (34 Mbps)'], [4050, 'E3 (34 Mbps)']]], ['Stacking', [[5000, 'Cisco StackWise'], [5050, 'Cisco StackWise Plus'], [5100, 'Cisco FlexStack'], [5150, 'Cisco FlexStack Plus'], [5200, 'Juniper VCP']]], ['Other', [[32767, 'Other']]]], default=1200),
        ),
        migrations.AddField(
            model_name='interface',
            name='lag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='member_interfaces', to='dcim.Interface', verbose_name='Parent LAG'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='mac_address',
            field=dcim.fields.MACAddressField(blank=True, null=True, verbose_name='MAC Address'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='mgmt_only',
            field=models.BooleanField(default=False, help_text='This interface is used only for out-of-band management', verbose_name='OOB Management'),
        ),
        migrations.AlterField(
            model_name='interfaceconnection',
            name='connection_status',
            field=models.BooleanField(choices=[[False, 'Planned'], [True, 'Connected']], default=True, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[['Virtual interfaces', [[0, 'Virtual'], [200, 'Link Aggregation Group (LAG)']]], ['Ethernet (fixed)', [[800, '100BASE-TX (10/100ME)'], [1000, '1000BASE-T (1GE)'], [1150, '10GBASE-T (10GE)']]], ['Ethernet (modular)', [[1050, 'GBIC (1GE)'], [1100, 'SFP (1GE)'], [1200, 'SFP+ (10GE)'], [1300, 'XFP (10GE)'], [1310, 'XENPAK (10GE)'], [1320, 'X2 (10GE)'], [1350, 'SFP28 (25GE)'], [1400, 'QSFP+ (40GE)'], [1500, 'CFP (100GE)'], [1600, 'QSFP28 (100GE)']]], ['FibreChannel', [[3010, 'SFP (1GFC)'], [3020, 'SFP (2GFC)'], [3040, 'SFP (4GFC)'], [3080, 'SFP+ (8GFC)'], [3160, 'SFP+ (16GFC)']]], ['Serial', [[4000, 'T1 (1.544 Mbps)'], [4010, 'E1 (2.048 Mbps)'], [4040, 'T3 (45 Mbps)'], [4050, 'E3 (34 Mbps)'], [4050, 'E3 (34 Mbps)']]], ['Stacking', [[5000, 'Cisco StackWise'], [5050, 'Cisco StackWise Plus'], [5100, 'Cisco FlexStack'], [5150, 'Cisco FlexStack Plus'], [5200, 'Juniper VCP']]], ['Other', [[32767, 'Other']]]], default=1200),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='mgmt_only',
            field=models.BooleanField(default=False, verbose_name='Management only'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='discovered',
            field=models.BooleanField(default=False, verbose_name='Discovered'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='part_id',
            field=models.CharField(blank=True, max_length=50, verbose_name='Part ID'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='serial',
            field=models.CharField(blank=True, max_length=50, verbose_name='Serial number'),
        ),
        migrations.AlterField(
            model_name='platform',
            name='rpc_client',
            field=models.CharField(blank=True, choices=[['juniper-junos', 'Juniper Junos (NETCONF)'], ['cisco-ios', 'Cisco IOS (SSH)'], ['opengear', 'Opengear (SSH)']], max_length=30, verbose_name='RPC client'),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='connection_status',
            field=models.NullBooleanField(choices=[[False, 'Planned'], [True, 'Connected']], default=True),
        ),
        migrations.AlterField(
            model_name='rack',
            name='desc_units',
            field=models.BooleanField(default=False, help_text='Units are numbered top-to-bottom', verbose_name='Descending units'),
        ),
        migrations.AlterField(
            model_name='rack',
            name='facility_id',
            field=utilities.fields.NullableCharField(blank=True, max_length=30, null=True, verbose_name='Facility ID'),
        ),
        migrations.AlterField(
            model_name='rack',
            name='type',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(100, '2-post frame'), (200, '4-post frame'), (300, '4-post cabinet'), (1000, 'Wall-mounted frame'), (1100, 'Wall-mounted cabinet')], null=True, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='rack',
            name='u_height',
            field=models.PositiveSmallIntegerField(default=42, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)], verbose_name='Height (U)'),
        ),
        migrations.AlterField(
            model_name='rack',
            name='width',
            field=models.PositiveSmallIntegerField(choices=[(19, '19 inches'), (23, '23 inches')], default=19, help_text='Rail-to-rail width', verbose_name='Width'),
        ),
        migrations.AlterField(
            model_name='site',
            name='asn',
            field=dcim.fields.ASNField(blank=True, null=True, verbose_name='ASN'),
        ),
        migrations.AlterField(
            model_name='site',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='Contact E-mail'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[['Virtual interfaces', [[0, 'Virtual'], [200, 'Link Aggregation Group (LAG)']]], ['Ethernet (fixed)', [[800, '100BASE-TX (10/100ME)'], [1000, '1000BASE-T (1GE)'], [1150, '10GBASE-T (10GE)']]], ['Ethernet (modular)', [[1050, 'GBIC (1GE)'], [1100, 'SFP (1GE)'], [1200, 'SFP+ (10GE)'], [1300, 'XFP (10GE)'], [1310, 'XENPAK (10GE)'], [1320, 'X2 (10GE)'], [1350, 'SFP28 (25GE)'], [1400, 'QSFP+ (40GE)'], [1500, 'CFP (100GE)'], [1600, 'QSFP28 (100GE)']]], ['Wireless', [[2600, 'IEEE 802.11a'], [2610, 'IEEE 802.11b/g'], [2620, 'IEEE 802.11n'], [2630, 'IEEE 802.11ac'], [2640, 'IEEE 802.11ad']]], ['FibreChannel', [[3010, 'SFP (1GFC)'], [3020, 'SFP (2GFC)'], [3040, 'SFP (4GFC)'], [3080, 'SFP+ (8GFC)'], [3160, 'SFP+ (16GFC)']]], ['Serial', [[4000, 'T1 (1.544 Mbps)'], [4010, 'E1 (2.048 Mbps)'], [4040, 'T3 (45 Mbps)'], [4050, 'E3 (34 Mbps)']]], ['Stacking', [[5000, 'Cisco StackWise'], [5050, 'Cisco StackWise Plus'], [5100, 'Cisco FlexStack'], [5150, 'Cisco FlexStack Plus'], [5200, 'Juniper VCP']]], ['Other', [[32767, 'Other']]]], default=1200),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[['Virtual interfaces', [[0, 'Virtual'], [200, 'Link Aggregation Group (LAG)']]], ['Ethernet (fixed)', [[800, '100BASE-TX (10/100ME)'], [1000, '1000BASE-T (1GE)'], [1150, '10GBASE-T (10GE)']]], ['Ethernet (modular)', [[1050, 'GBIC (1GE)'], [1100, 'SFP (1GE)'], [1200, 'SFP+ (10GE)'], [1300, 'XFP (10GE)'], [1310, 'XENPAK (10GE)'], [1320, 'X2 (10GE)'], [1350, 'SFP28 (25GE)'], [1400, 'QSFP+ (40GE)'], [1500, 'CFP (100GE)'], [1600, 'QSFP28 (100GE)']]], ['Wireless', [[2600, 'IEEE 802.11a'], [2610, 'IEEE 802.11b/g'], [2620, 'IEEE 802.11n'], [2630, 'IEEE 802.11ac'], [2640, 'IEEE 802.11ad']]], ['FibreChannel', [[3010, 'SFP (1GFC)'], [3020, 'SFP (2GFC)'], [3040, 'SFP (4GFC)'], [3080, 'SFP+ (8GFC)'], [3160, 'SFP+ (16GFC)']]], ['Serial', [[4000, 'T1 (1.544 Mbps)'], [4010, 'E1 (2.048 Mbps)'], [4040, 'T3 (45 Mbps)'], [4050, 'E3 (34 Mbps)']]], ['Stacking', [[5000, 'Cisco StackWise'], [5050, 'Cisco StackWise Plus'], [5100, 'Cisco FlexStack'], [5150, 'Cisco FlexStack Plus'], [5200, 'Juniper VCP']]], ['Other', [[32767, 'Other']]]], default=1200),
        ),
        migrations.AddField(
            model_name='interface',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='mtu',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='MTU'),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='asset_tag',
            field=utilities.fields.NullableCharField(blank=True, help_text='A unique tag used to identify this item', max_length=50, null=True, unique=True, verbose_name='Asset tag'),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterModelOptions(
            name='device',
            options={'ordering': ['name'], 'permissions': (('napalm_read', 'Read-only access to devices via NAPALM'), ('napalm_write', 'Read/write access to devices via NAPALM'))},
        ),
        migrations.AddField(
            model_name='platform',
            name='napalm_driver',
            field=models.CharField(blank=True, help_text='The name of the NAPALM driver to use when interacting with devices.', max_length=50, verbose_name='NAPALM driver'),
        ),
        migrations.AlterField(
            model_name='platform',
            name='rpc_client',
            field=models.CharField(blank=True, choices=[['juniper-junos', 'Juniper Junos (NETCONF)'], ['cisco-ios', 'Cisco IOS (SSH)'], ['opengear', 'Opengear (SSH)']], max_length=30, verbose_name='Legacy RPC client'),
        ),
        migrations.RunPython(
            code=rpc_client_to_napalm_driver,
        ),
        migrations.AlterField(
            model_name='interface',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[['Virtual interfaces', [[0, 'Virtual'], [200, 'Link Aggregation Group (LAG)']]], ['Ethernet (fixed)', [[800, '100BASE-TX (10/100ME)'], [1000, '1000BASE-T (1GE)'], [1150, '10GBASE-T (10GE)'], [1170, '10GBASE-CX4 (10GE)']]], ['Ethernet (modular)', [[1050, 'GBIC (1GE)'], [1100, 'SFP (1GE)'], [1200, 'SFP+ (10GE)'], [1300, 'XFP (10GE)'], [1310, 'XENPAK (10GE)'], [1320, 'X2 (10GE)'], [1350, 'SFP28 (25GE)'], [1400, 'QSFP+ (40GE)'], [1500, 'CFP (100GE)'], [1600, 'QSFP28 (100GE)']]], ['Wireless', [[2600, 'IEEE 802.11a'], [2610, 'IEEE 802.11b/g'], [2620, 'IEEE 802.11n'], [2630, 'IEEE 802.11ac'], [2640, 'IEEE 802.11ad']]], ['FibreChannel', [[3010, 'SFP (1GFC)'], [3020, 'SFP (2GFC)'], [3040, 'SFP (4GFC)'], [3080, 'SFP+ (8GFC)'], [3160, 'SFP+ (16GFC)']]], ['Serial', [[4000, 'T1 (1.544 Mbps)'], [4010, 'E1 (2.048 Mbps)'], [4040, 'T3 (45 Mbps)'], [4050, 'E3 (34 Mbps)']]], ['Stacking', [[5000, 'Cisco StackWise'], [5050, 'Cisco StackWise Plus'], [5100, 'Cisco FlexStack'], [5150, 'Cisco FlexStack Plus'], [5200, 'Juniper VCP']]], ['Other', [[32767, 'Other']]]], default=1200),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='form_factor',
            field=models.PositiveSmallIntegerField(choices=[['Virtual interfaces', [[0, 'Virtual'], [200, 'Link Aggregation Group (LAG)']]], ['Ethernet (fixed)', [[800, '100BASE-TX (10/100ME)'], [1000, '1000BASE-T (1GE)'], [1150, '10GBASE-T (10GE)'], [1170, '10GBASE-CX4 (10GE)']]], ['Ethernet (modular)', [[1050, 'GBIC (1GE)'], [1100, 'SFP (1GE)'], [1200, 'SFP+ (10GE)'], [1300, 'XFP (10GE)'], [1310, 'XENPAK (10GE)'], [1320, 'X2 (10GE)'], [1350, 'SFP28 (25GE)'], [1400, 'QSFP+ (40GE)'], [1500, 'CFP (100GE)'], [1600, 'QSFP28 (100GE)']]], ['Wireless', [[2600, 'IEEE 802.11a'], [2610, 'IEEE 802.11b/g'], [2620, 'IEEE 802.11n'], [2630, 'IEEE 802.11ac'], [2640, 'IEEE 802.11ad']]], ['FibreChannel', [[3010, 'SFP (1GFC)'], [3020, 'SFP (2GFC)'], [3040, 'SFP (4GFC)'], [3080, 'SFP+ (8GFC)'], [3160, 'SFP+ (16GFC)']]], ['Serial', [[4000, 'T1 (1.544 Mbps)'], [4010, 'E1 (2.048 Mbps)'], [4040, 'T3 (45 Mbps)'], [4050, 'E3 (34 Mbps)']]], ['Stacking', [[5000, 'Cisco StackWise'], [5050, 'Cisco StackWise Plus'], [5100, 'Cisco FlexStack'], [5150, 'Cisco FlexStack Plus'], [5200, 'Juniper VCP']]], ['Other', [[32767, 'Other']]]], default=1200),
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='consoleporttemplate',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='consoleserverporttemplate',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='devicebaytemplate',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='interface',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='name',
            field=models.CharField(max_length=50),
        ),
    ]
