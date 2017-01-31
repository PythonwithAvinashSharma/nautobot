from rest_framework import serializers

from ipam.models import IPAddress
from dcim.models import (
    ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay, DeviceType,
    DeviceRole, Interface, InterfaceConnection, InterfaceTemplate, Manufacturer, Module, Platform, PowerOutlet,
    PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack, RackGroup, RackRole, Site, SUBDEVICE_ROLE_CHILD,
    SUBDEVICE_ROLE_PARENT,
)
from extras.api.serializers import CustomFieldValueSerializer
from tenancy.api.serializers import NestedTenantSerializer


#
# Sites
#

class SiteSerializer(serializers.ModelSerializer):
    tenant = NestedTenantSerializer()
    custom_field_values = CustomFieldValueSerializer(many=True)

    class Meta:
        model = Site
        fields = [
            'id', 'name', 'slug', 'tenant', 'facility', 'asn', 'physical_address', 'shipping_address', 'contact_name',
            'contact_phone', 'contact_email', 'comments', 'custom_field_values', 'count_prefixes', 'count_vlans',
            'count_racks', 'count_devices', 'count_circuits',
        ]


class NestedSiteSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:site-detail')

    class Meta:
        model = Site
        fields = ['id', 'url', 'name', 'slug']


class WritableSiteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Site
        fields = [
            'id', 'name', 'slug', 'tenant', 'facility', 'asn', 'physical_address', 'shipping_address', 'contact_name',
            'contact_phone', 'contact_email', 'comments',
        ]


#
# Rack groups
#

class RackGroupSerializer(serializers.ModelSerializer):
    site = NestedSiteSerializer()

    class Meta:
        model = RackGroup
        fields = ['id', 'name', 'slug', 'site']


class NestedRackGroupSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackgroup-detail')

    class Meta:
        model = RackGroup
        fields = ['id', 'url', 'name', 'slug']


class WritableRackGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = RackGroup
        fields = ['id', 'name', 'slug', 'site']


#
# Rack roles
#

class RackRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = RackRole
        fields = ['id', 'name', 'slug', 'color']


class NestedRackRoleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rackrole-detail')

    class Meta:
        model = RackRole
        fields = ['id', 'url', 'name', 'slug']


#
# Racks
#


class RackSerializer(serializers.ModelSerializer):
    site = NestedSiteSerializer()
    group = NestedRackGroupSerializer()
    tenant = NestedTenantSerializer()
    role = NestedRackRoleSerializer()
    custom_field_values = CustomFieldValueSerializer(many=True)

    class Meta:
        model = Rack
        fields = [
            'id', 'name', 'facility_id', 'display_name', 'site', 'group', 'tenant', 'role', 'type', 'width', 'u_height',
            'desc_units', 'comments', 'custom_field_values',
        ]


class NestedRackSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:rack-detail')

    class Meta:
        model = Rack
        fields = ['id', 'url', 'name', 'display_name']


class WritableRackSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rack
        fields = [
            'id', 'name', 'facility_id', 'site', 'group', 'tenant', 'role', 'type', 'width', 'u_height', 'desc_units',
            'comments',
        ]


#
# Manufacturers
#

class ManufacturerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'slug']


class NestedManufacturerSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:manufacturer-detail')

    class Meta:
        model = Manufacturer
        fields = ['id', 'url', 'name', 'slug']


#
# Device types
#

class DeviceTypeSerializer(serializers.ModelSerializer):
    manufacturer = NestedManufacturerSerializer()
    subdevice_role = serializers.SerializerMethodField()
    instance_count = serializers.IntegerField(source='instances.count', read_only=True)
    custom_field_values = CustomFieldValueSerializer(many=True)

    class Meta:
        model = DeviceType
        fields = [
            'id', 'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'interface_ordering',
            'is_console_server', 'is_pdu', 'is_network_device', 'subdevice_role', 'comments', 'custom_field_values',
            'instance_count',
        ]

    def get_subdevice_role(self, obj):
        return {
            SUBDEVICE_ROLE_PARENT: 'parent',
            SUBDEVICE_ROLE_CHILD: 'child',
            None: None,
        }[obj.subdevice_role]


class NestedDeviceTypeSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicetype-detail')
    manufacturer = NestedManufacturerSerializer()

    class Meta:
        model = DeviceType
        fields = ['id', 'url', 'manufacturer', 'model', 'slug']


class WritableDeviceTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceType
        fields = [
            'id', 'manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'interface_ordering',
            'is_console_server', 'is_pdu', 'is_network_device', 'subdevice_role', 'comments',
        ]


class ConsolePortTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsolePortTemplate
        fields = ['id', 'name']


class ConsoleServerPortTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = ['id', 'name']


class PowerPortTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PowerPortTemplate
        fields = ['id', 'name']


class PowerOutletTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PowerOutletTemplate
        fields = ['id', 'name']


class InterfaceTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = InterfaceTemplate
        fields = ['id', 'name', 'form_factor', 'mgmt_only']


class DeviceBayTemplateSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceBay
        fields = ['id', 'name',]


#
# Device roles
#

class DeviceRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceRole
        fields = ['id', 'name', 'slug', 'color']


class NestedDeviceRoleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicerole-detail')

    class Meta:
        model = DeviceRole
        fields = ['id', 'url', 'name', 'slug']


#
# Platforms
#

class PlatformSerializer(serializers.ModelSerializer):

    class Meta:
        model = Platform
        fields = ['id', 'name', 'slug', 'rpc_client']


class NestedPlatformSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:platform-detail')

    class Meta:
        model = Platform
        fields = ['id', 'url', 'name', 'slug']


#
# Devices
#

# Cannot import ipam.api.NestedIPAddressSerializer due to circular dependency
class DeviceIPAddressSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:ipaddress-detail')

    class Meta:
        model = IPAddress
        fields = ['id', 'url', 'family', 'address']


class DeviceSerializer(serializers.ModelSerializer):
    device_type = NestedDeviceTypeSerializer()
    device_role = NestedDeviceRoleSerializer()
    tenant = NestedTenantSerializer()
    platform = NestedPlatformSerializer()
    rack = NestedRackSerializer()
    primary_ip = DeviceIPAddressSerializer()
    primary_ip4 = DeviceIPAddressSerializer()
    primary_ip6 = DeviceIPAddressSerializer()
    parent_device = serializers.SerializerMethodField()
    custom_field_values = CustomFieldValueSerializer(many=True)

    class Meta:
        model = Device
        fields = [
            'id', 'name', 'display_name', 'device_type', 'device_role', 'tenant', 'platform', 'serial',  'asset_tag',
            'rack', 'position', 'face', 'parent_device', 'status', 'primary_ip', 'primary_ip4', 'primary_ip6',
            'comments', 'custom_field_values',
        ]

    def get_parent_device(self, obj):
        try:
            device_bay = obj.parent_bay
        except DeviceBay.DoesNotExist:
            return None
        return {
            'id': device_bay.device.pk,
            'name': device_bay.device.name,
            'device_bay': {
                'id': device_bay.pk,
                'name': device_bay.name,
            }
        }


class NestedDeviceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:device-detail')

    class Meta:
        model = Device
        fields = ['id', 'url', 'name', 'display_name']


class WritableDeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Device
        fields = [
            'id', 'name', 'device_type', 'device_role', 'tenant', 'platform', 'serial',  'asset_tag', 'rack',
            'position', 'face', 'status', 'primary_ip4', 'primary_ip6', 'comments',
        ]


#
# Console server ports
#

class ConsoleServerPortSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = ConsoleServerPort
        fields = ['id', 'device', 'name', 'connected_console']


class DeviceConsoleServerPortSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleserverport-detail')

    class Meta:
        model = ConsoleServerPort
        fields = ['id', 'url', 'name', 'connected_console']
        read_only_fields = ['connected_console']


#
# Console ports
#

class ConsolePortSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer(read_only=True)
    cs_port = ConsoleServerPortSerializer()

    class Meta:
        model = ConsolePort
        fields = ['id', 'device', 'name', 'cs_port', 'connection_status']


class DeviceConsolePortSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:consoleport-detail')

    class Meta:
        model = ConsolePort
        fields = ['id', 'url', 'name', 'cs_port', 'connection_status']
        read_only_fields = ['cs_port', 'connection_status']


#
# Power outlets
#

class PowerOutletSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer(read_only=True)

    class Meta:
        model = PowerOutlet
        fields = ['id', 'device', 'name', 'connected_port']


class DevicePowerOutletSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:poweroutlet-detail')

    class Meta:
        model = PowerOutlet
        fields = ['id', 'url', 'name', 'connected_port']
        read_only_fields = ['connected_port']


#
# Power ports
#

class PowerPortSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer(read_only=True)
    power_outlet = PowerOutletSerializer()

    class Meta:
        model = PowerPort
        fields = ['id', 'device', 'name', 'power_outlet', 'connection_status']


class DevicePowerPortSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:powerport-detail')

    class Meta:
        model = PowerPort
        fields = ['id', 'url', 'name', 'power_outlet', 'connection_status']
        read_only_fields = ['power_outlet', 'connection_status']


#
# Interfaces
#


class InterfaceSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer(read_only=True)
    connection = serializers.SerializerMethodField(read_only=True)
    connected_interface = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Interface
        fields = [
            'id', 'device', 'name', 'form_factor', 'mac_address', 'mgmt_only', 'description', 'connection',
            'connected_interface',
        ]

    def get_connection(self, obj):
        if obj.connection:
            return NestedInterfaceConnectionSerializer(obj.connection, context=self.context).data
        return None

    def get_connected_interface(self, obj):
        if obj.connected_interface:
            return PeerInterfaceSerializer(obj.connected_interface, context=self.context).data
        return None


class PeerInterfaceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')
    device = NestedDeviceSerializer()

    class Meta:
        model = Interface
        fields = ['id', 'url', 'device', 'name', 'form_factor', 'mac_address', 'mgmt_only', 'description']


class DeviceInterfaceSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interface-detail')
    connection = serializers.SerializerMethodField()

    class Meta:
        model = Interface
        fields = ['id', 'url', 'name', 'form_factor', 'mac_address', 'mgmt_only', 'description', 'connection']

    def get_connection(self, obj):
        if obj.connection:
            return NestedInterfaceConnectionSerializer(obj.connection, context=self.context).data
        return None


#
# Interface connections
#

class InterfaceConnectionSerializer(serializers.ModelSerializer):
    interface_a = PeerInterfaceSerializer()
    interface_b = PeerInterfaceSerializer()

    class Meta:
        model = InterfaceConnection
        fields = ['id', 'interface_a', 'interface_b', 'connection_status']


class NestedInterfaceConnectionSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:interfaceconnection-detail')

    class Meta:
        model = InterfaceConnection
        fields = ['id', 'url', 'connection_status']


class WritableInterfaceConnectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = InterfaceConnection
        fields = ['id', 'interface_a', 'interface_b', 'connection_status']


#
# Device bays
#

class DeviceBaySerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer(read_only=True)
    installed_device = NestedDeviceSerializer()

    class Meta:
        model = DeviceBay
        fields = ['id', 'device', 'name', 'installed_device']


class DeviceDeviceBaySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:devicebay-detail')

    class Meta:
        model = DeviceBay
        fields = ['id', 'url', 'name', 'installed_device']
        read_only_fields = ['installed_device']


#
# Modules
#

class ModuleSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer(read_only=True)
    manufacturer = NestedManufacturerSerializer()

    class Meta:
        model = Module
        fields = ['id', 'device', 'parent', 'name', 'manufacturer', 'part_id', 'serial', 'discovered']


class DeviceModuleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='dcim-api:module-detail')
    manufacturer = NestedManufacturerSerializer()

    class Meta:
        model = Module
        fields = ['id', 'url', 'name', 'manufacturer', 'part_id', 'serial', 'discovered']
