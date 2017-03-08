from rest_framework import serializers

from dcim.api.serializers import NestedDeviceSerializer, InterfaceSerializer, NestedSiteSerializer
from extras.api.customfields import CustomFieldModelSerializer
from ipam.models import (
    Aggregate, IPAddress, IPADDRESS_STATUS_CHOICES, IP_PROTOCOL_CHOICES, Prefix, PREFIX_STATUS_CHOICES, RIR, Role,
    Service, VLAN, VLAN_STATUS_CHOICES, VLANGroup, VRF,
)
from tenancy.api.serializers import NestedTenantSerializer
from utilities.api import ChoiceFieldSerializer


#
# VRFs
#

class VRFSerializer(CustomFieldModelSerializer):
    tenant = NestedTenantSerializer()

    class Meta:
        model = VRF
        fields = ['id', 'name', 'rd', 'tenant', 'enforce_unique', 'description', 'custom_fields']


class NestedVRFSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vrf-detail')

    class Meta:
        model = VRF
        fields = ['id', 'url', 'name', 'rd']


class WritableVRFSerializer(serializers.ModelSerializer):

    class Meta:
        model = VRF
        fields = ['id', 'name', 'rd', 'tenant', 'enforce_unique', 'description']


#
# Roles
#

class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'weight']


class NestedRoleSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:role-detail')

    class Meta:
        model = Role
        fields = ['id', 'url', 'name', 'slug']


#
# RIRs
#

class RIRSerializer(serializers.ModelSerializer):

    class Meta:
        model = RIR
        fields = ['id', 'name', 'slug', 'is_private']


class NestedRIRSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:rir-detail')

    class Meta:
        model = RIR
        fields = ['id', 'url', 'name', 'slug']


#
# Aggregates
#

class AggregateSerializer(CustomFieldModelSerializer):
    rir = NestedRIRSerializer()

    class Meta:
        model = Aggregate
        fields = ['id', 'family', 'prefix', 'rir', 'date_added', 'description', 'custom_fields']


class NestedAggregateSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:aggregate-detail')

    class Meta(AggregateSerializer.Meta):
        model = Aggregate
        fields = ['id', 'url', 'family', 'prefix']


class WritableAggregateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Aggregate
        fields = ['id', 'family', 'prefix', 'rir', 'date_added', 'description']


#
# VLAN groups
#

class VLANGroupSerializer(serializers.ModelSerializer):
    site = NestedSiteSerializer()

    class Meta:
        model = VLANGroup
        fields = ['id', 'name', 'slug', 'site']


class NestedVLANGroupSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlangroup-detail')

    class Meta:
        model = VLANGroup
        fields = ['id', 'url', 'name', 'slug']


class WritableVLANGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = VLANGroup
        fields = ['id', 'name', 'slug', 'site']


#
# VLANs
#

class VLANSerializer(CustomFieldModelSerializer):
    site = NestedSiteSerializer()
    group = NestedVLANGroupSerializer()
    tenant = NestedTenantSerializer()
    status = ChoiceFieldSerializer(choices=VLAN_STATUS_CHOICES)
    role = NestedRoleSerializer()

    class Meta:
        model = VLAN
        fields = [
            'id', 'site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description', 'display_name',
            'custom_fields',
        ]


class NestedVLANSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:vlan-detail')

    class Meta:
        model = VLAN
        fields = ['id', 'url', 'vid', 'name', 'display_name']


class WritableVLANSerializer(serializers.ModelSerializer):

    class Meta:
        model = VLAN
        fields = [
            'id', 'site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description',
        ]


#
# Prefixes
#

class PrefixSerializer(CustomFieldModelSerializer):
    site = NestedSiteSerializer()
    vrf = NestedVRFSerializer()
    tenant = NestedTenantSerializer()
    vlan = NestedVLANSerializer()
    status = ChoiceFieldSerializer(choices=PREFIX_STATUS_CHOICES)
    role = NestedRoleSerializer()

    class Meta:
        model = Prefix
        fields = [
            'id', 'family', 'prefix', 'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'is_pool', 'description',
            'custom_fields',
        ]


class NestedPrefixSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:prefix-detail')

    class Meta:
        model = Prefix
        fields = ['id', 'url', 'family', 'prefix']


class WritablePrefixSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prefix
        fields = [
            'id', 'family', 'prefix', 'site', 'vrf', 'tenant', 'vlan', 'status', 'role', 'is_pool', 'description',
        ]


#
# IP addresses
#

class IPAddressSerializer(CustomFieldModelSerializer):
    vrf = NestedVRFSerializer()
    tenant = NestedTenantSerializer()
    status = ChoiceFieldSerializer(choices=IPADDRESS_STATUS_CHOICES)
    interface = InterfaceSerializer()

    class Meta:
        model = IPAddress
        fields = [
            'id', 'family', 'address', 'vrf', 'tenant', 'status', 'interface', 'description', 'nat_inside',
            'nat_outside', 'custom_fields',
        ]


class NestedIPAddressSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='ipam-api:ipaddress-detail')

    class Meta:
        model = IPAddress
        fields = ['id', 'url', 'family', 'address']

IPAddressSerializer._declared_fields['nat_inside'] = NestedIPAddressSerializer()
IPAddressSerializer._declared_fields['nat_outside'] = NestedIPAddressSerializer()


class WritableIPAddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = IPAddress
        fields = ['id', 'family', 'address', 'vrf', 'tenant', 'status', 'interface', 'description', 'nat_inside']


#
# Services
#

class ServiceSerializer(serializers.ModelSerializer):
    device = NestedDeviceSerializer()
    protocol = ChoiceFieldSerializer(choices=IP_PROTOCOL_CHOICES)
    ipaddresses = NestedIPAddressSerializer(many=True)

    class Meta:
        model = Service
        fields = ['id', 'device', 'name', 'port', 'protocol', 'ipaddresses', 'description']


class WritableServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ['id', 'device', 'name', 'port', 'protocol', 'ipaddresses', 'description']
