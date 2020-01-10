import django_filters
from django.contrib.auth.models import User
from django.db.models import Q

from extras.filters import CustomFieldFilterSet, LocalConfigContextFilterSet, CreatedUpdatedFilterSet
from tenancy.filtersets import TenancyFilterSet
from tenancy.models import Tenant
from utilities.constants import COLOR_CHOICES
from utilities.filters import (
    MultiValueCharFilter, MultiValueMACAddressFilter, MultiValueNumberFilter, NameSlugSearchFilterSet, NumericInFilter,
    TagFilter, TreeNodeMultipleChoiceFilter,
)
from virtualization.models import Cluster
from .choices import *
from .constants import *
from .models import (
    Cable, ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceBay,
    DeviceBayTemplate, DeviceRole, DeviceType, FrontPort, FrontPortTemplate, Interface, InterfaceTemplate,
    InventoryItem, Manufacturer, Platform, PowerFeed, PowerOutlet, PowerOutletTemplate, PowerPanel, PowerPort,
    PowerPortTemplate, Rack, RackGroup, RackReservation, RackRole, RearPort, RearPortTemplate, Region, Site,
    VirtualChassis,
)


__all__ = (
    'CableFilterSet',
    'ConsoleConnectionFilterSet',
    'ConsolePortFilterSet',
    'ConsolePortTemplateFilterSet',
    'ConsoleServerPortFilterSet',
    'ConsoleServerPortTemplateFilterSet',
    'DeviceBayFilterSet',
    'DeviceBayTemplateFilterSet',
    'DeviceFilterSet',
    'DeviceRoleFilterSet',
    'DeviceTypeFilterSet',
    'FrontPortFilterSet',
    'FrontPortTemplateFilterSet',
    'InterfaceConnectionFilterSet',
    'InterfaceFilterSet',
    'InterfaceTemplateFilterSet',
    'InventoryItemFilterSet',
    'ManufacturerFilterSet',
    'PlatformFilterSet',
    'PowerConnectionFilterSet',
    'PowerFeedFilterSet',
    'PowerOutletFilterSet',
    'PowerOutletTemplateFilterSet',
    'PowerPanelFilterSet',
    'PowerPortFilterSet',
    'PowerPortTemplateFilterSet',
    'RackFilterSet',
    'RackGroupFilterSet',
    'RackReservationFilterSet',
    'RackRoleFilterSet',
    'RearPortFilterSet',
    'RearPortTemplateFilterSet',
    'RegionFilterSet',
    'SiteFilterSet',
    'VirtualChassisFilterSet',
)


class RegionFilterSet(NameSlugSearchFilterSet):
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Region.objects.all(),
        label='Parent region (ID)',
    )
    parent = django_filters.ModelMultipleChoiceFilter(
        field_name='parent__slug',
        queryset=Region.objects.all(),
        to_field_name='slug',
        label='Parent region (slug)',
    )

    class Meta:
        model = Region
        fields = ['id', 'name', 'slug']


class SiteFilterSet(TenancyFilterSet, CustomFieldFilterSet, CreatedUpdatedFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=SiteStatusChoices,
        null_value=None
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='region__in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='region__in',
        to_field_name='slug',
        label='Region (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = Site
        fields = [
            'id', 'name', 'slug', 'facility', 'asn', 'latitude', 'longitude', 'contact_name', 'contact_phone',
            'contact_email',
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(facility__icontains=value) |
            Q(description__icontains=value) |
            Q(physical_address__icontains=value) |
            Q(shipping_address__icontains=value) |
            Q(contact_name__icontains=value) |
            Q(contact_phone__icontains=value) |
            Q(contact_email__icontains=value) |
            Q(comments__icontains=value)
        )
        try:
            qs_filter |= Q(asn=int(value.strip()))
        except ValueError:
            pass
        return queryset.filter(qs_filter)


class RackGroupFilterSet(NameSlugSearchFilterSet):
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region__in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region__in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )

    class Meta:
        model = RackGroup
        fields = ['id', 'name', 'slug']


class RackRoleFilterSet(NameSlugSearchFilterSet):

    class Meta:
        model = RackRole
        fields = ['id', 'name', 'slug', 'color']


class RackFilterSet(TenancyFilterSet, CustomFieldFilterSet, CreatedUpdatedFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region__in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region__in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RackGroup.objects.all(),
        label='Group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='group__slug',
        queryset=RackGroup.objects.all(),
        to_field_name='slug',
        label='Group',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=RackStatusChoices,
        null_value=None
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        queryset=RackRole.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='role__slug',
        queryset=RackRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    serial = django_filters.CharFilter(
        lookup_expr='iexact'
    )
    tag = TagFilter()

    class Meta:
        model = Rack
        fields = [
            'id', 'name', 'facility_id', 'asset_tag', 'type', 'width', 'u_height', 'desc_units',
            'outer_width', 'outer_depth', 'outer_unit',
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(facility_id__icontains=value) |
            Q(serial__icontains=value.strip()) |
            Q(asset_tag__icontains=value.strip()) |
            Q(comments__icontains=value)
        )


class RackReservationFilterSet(TenancyFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Rack.objects.all(),
        label='Rack (ID)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='rack__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site (slug)',
    )
    group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack__group',
        queryset=RackGroup.objects.all(),
        label='Group (ID)',
    )
    group = django_filters.ModelMultipleChoiceFilter(
        field_name='rack__group__slug',
        queryset=RackGroup.objects.all(),
        to_field_name='slug',
        label='Group',
    )
    user_id = django_filters.ModelMultipleChoiceFilter(
        queryset=User.objects.all(),
        label='User (ID)',
    )
    user = django_filters.ModelMultipleChoiceFilter(
        field_name='user',
        queryset=User.objects.all(),
        to_field_name='username',
        label='User (name)',
    )

    class Meta:
        model = RackReservation
        fields = ['created']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(rack__name__icontains=value) |
            Q(rack__facility_id__icontains=value) |
            Q(user__username__icontains=value) |
            Q(description__icontains=value)
        )


class ManufacturerFilterSet(NameSlugSearchFilterSet):

    class Meta:
        model = Manufacturer
        fields = ['id', 'name', 'slug']


class DeviceTypeFilterSet(CustomFieldFilterSet, CreatedUpdatedFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Manufacturer.objects.all(),
        label='Manufacturer (ID)',
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label='Manufacturer (slug)',
    )
    console_ports = django_filters.BooleanFilter(
        method='_console_ports',
        label='Has console ports',
    )
    console_server_ports = django_filters.BooleanFilter(
        method='_console_server_ports',
        label='Has console server ports',
    )
    power_ports = django_filters.BooleanFilter(
        method='_power_ports',
        label='Has power ports',
    )
    power_outlets = django_filters.BooleanFilter(
        method='_power_outlets',
        label='Has power outlets',
    )
    interfaces = django_filters.BooleanFilter(
        method='_interfaces',
        label='Has interfaces',
    )
    pass_through_ports = django_filters.BooleanFilter(
        method='_pass_through_ports',
        label='Has pass-through ports',
    )
    tag = TagFilter()

    class Meta:
        model = DeviceType
        fields = [
            'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'subdevice_role',
        ]

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(manufacturer__name__icontains=value) |
            Q(model__icontains=value) |
            Q(part_number__icontains=value) |
            Q(comments__icontains=value)
        )

    def _console_ports(self, queryset, name, value):
        return queryset.exclude(consoleport_templates__isnull=value)

    def _console_server_ports(self, queryset, name, value):
        return queryset.exclude(consoleserverport_templates__isnull=value)

    def _power_ports(self, queryset, name, value):
        return queryset.exclude(powerport_templates__isnull=value)

    def _power_outlets(self, queryset, name, value):
        return queryset.exclude(poweroutlet_templates__isnull=value)

    def _interfaces(self, queryset, name, value):
        return queryset.exclude(interface_templates__isnull=value)

    def _pass_through_ports(self, queryset, name, value):
        return queryset.exclude(
            frontport_templates__isnull=value,
            rearport_templates__isnull=value
        )


class DeviceTypeComponentFilterSet(NameSlugSearchFilterSet):
    devicetype_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceType.objects.all(),
        field_name='device_type_id',
        label='Device type (ID)',
    )


class ConsolePortTemplateFilterSet(DeviceTypeComponentFilterSet):

    class Meta:
        model = ConsolePortTemplate
        fields = ['id', 'name', 'type']


class ConsoleServerPortTemplateFilterSet(DeviceTypeComponentFilterSet):

    class Meta:
        model = ConsoleServerPortTemplate
        fields = ['id', 'name', 'type']


class PowerPortTemplateFilterSet(DeviceTypeComponentFilterSet):

    class Meta:
        model = PowerPortTemplate
        fields = ['id', 'name', 'type', 'maximum_draw', 'allocated_draw']


class PowerOutletTemplateFilterSet(DeviceTypeComponentFilterSet):

    class Meta:
        model = PowerOutletTemplate
        fields = ['id', 'name', 'type', 'feed_leg']


class InterfaceTemplateFilterSet(DeviceTypeComponentFilterSet):

    class Meta:
        model = InterfaceTemplate
        fields = ['id', 'name', 'type', 'mgmt_only']


class FrontPortTemplateFilterSet(DeviceTypeComponentFilterSet):

    class Meta:
        model = FrontPortTemplate
        fields = ['id', 'name', 'type']


class RearPortTemplateFilterSet(DeviceTypeComponentFilterSet):

    class Meta:
        model = RearPortTemplate
        fields = ['id', 'name', 'type', 'positions']


class DeviceBayTemplateFilterSet(DeviceTypeComponentFilterSet):

    class Meta:
        model = DeviceBayTemplate
        fields = ['id', 'name']


class DeviceRoleFilterSet(NameSlugSearchFilterSet):

    class Meta:
        model = DeviceRole
        fields = ['id', 'name', 'slug', 'color', 'vm_role']


class PlatformFilterSet(NameSlugSearchFilterSet):
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer',
        queryset=Manufacturer.objects.all(),
        label='Manufacturer (ID)',
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label='Manufacturer (slug)',
    )

    class Meta:
        model = Platform
        fields = ['id', 'name', 'slug', 'napalm_driver']


class DeviceFilterSet(LocalConfigContextFilterSet, TenancyFilterSet, CustomFieldFilterSet, CreatedUpdatedFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__manufacturer',
        queryset=Manufacturer.objects.all(),
        label='Manufacturer (ID)',
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label='Manufacturer (slug)',
    )
    device_type_id = django_filters.ModelMultipleChoiceFilter(
        queryset=DeviceType.objects.all(),
        label='Device type (ID)',
    )
    role_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device_role_id',
        queryset=DeviceRole.objects.all(),
        label='Role (ID)',
    )
    role = django_filters.ModelMultipleChoiceFilter(
        field_name='device_role__slug',
        queryset=DeviceRole.objects.all(),
        to_field_name='slug',
        label='Role (slug)',
    )
    platform_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Platform.objects.all(),
        label='Platform (ID)',
    )
    platform = django_filters.ModelMultipleChoiceFilter(
        field_name='platform__slug',
        queryset=Platform.objects.all(),
        to_field_name='slug',
        label='Platform (slug)',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region__in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region__in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site name (slug)',
    )
    rack_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack__group',
        queryset=RackGroup.objects.all(),
        label='Rack group (ID)',
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack',
        queryset=Rack.objects.all(),
        label='Rack (ID)',
    )
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Cluster.objects.all(),
        label='VM cluster (ID)',
    )
    model = django_filters.ModelMultipleChoiceFilter(
        field_name='device_type__slug',
        queryset=DeviceType.objects.all(),
        to_field_name='slug',
        label='Device model (slug)',
    )
    status = django_filters.MultipleChoiceFilter(
        choices=DeviceStatusChoices,
        null_value=None
    )
    is_full_depth = django_filters.BooleanFilter(
        field_name='device_type__is_full_depth',
        label='Is full depth',
    )
    mac_address = MultiValueMACAddressFilter(
        field_name='interfaces__mac_address',
        label='MAC address',
    )
    serial = django_filters.CharFilter(
        lookup_expr='iexact'
    )
    has_primary_ip = django_filters.BooleanFilter(
        method='_has_primary_ip',
        label='Has a primary IP',
    )
    virtual_chassis_id = django_filters.ModelMultipleChoiceFilter(
        field_name='virtual_chassis',
        queryset=VirtualChassis.objects.all(),
        label='Virtual chassis (ID)',
    )
    virtual_chassis_member = django_filters.BooleanFilter(
        method='_virtual_chassis_member',
        label='Is a virtual chassis member'
    )
    console_ports = django_filters.BooleanFilter(
        method='_console_ports',
        label='Has console ports',
    )
    console_server_ports = django_filters.BooleanFilter(
        method='_console_server_ports',
        label='Has console server ports',
    )
    power_ports = django_filters.BooleanFilter(
        method='_power_ports',
        label='Has power ports',
    )
    power_outlets = django_filters.BooleanFilter(
        method='_power_outlets',
        label='Has power outlets',
    )
    interfaces = django_filters.BooleanFilter(
        method='_interfaces',
        label='Has interfaces',
    )
    pass_through_ports = django_filters.BooleanFilter(
        method='_pass_through_ports',
        label='Has pass-through ports',
    )
    tag = TagFilter()

    class Meta:
        model = Device
        fields = ['id', 'name', 'asset_tag', 'face', 'position', 'vc_position', 'vc_priority']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(serial__icontains=value.strip()) |
            Q(inventory_items__serial__icontains=value.strip()) |
            Q(asset_tag__icontains=value.strip()) |
            Q(comments__icontains=value)
        ).distinct()

    def _has_primary_ip(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(primary_ip4__isnull=False) |
                Q(primary_ip6__isnull=False)
            )
        else:
            return queryset.exclude(
                Q(primary_ip4__isnull=False) |
                Q(primary_ip6__isnull=False)
            )

    def _virtual_chassis_member(self, queryset, name, value):
        return queryset.exclude(virtual_chassis__isnull=value)

    def _console_ports(self, queryset, name, value):
        return queryset.exclude(consoleports__isnull=value)

    def _console_server_ports(self, queryset, name, value):
        return queryset.exclude(consoleserverports__isnull=value)

    def _power_ports(self, queryset, name, value):
        return queryset.exclude(powerports__isnull=value)

    def _power_outlets(self, queryset, name, value):
        return queryset.exclude(poweroutlets__isnull=value)

    def _interfaces(self, queryset, name, value):
        return queryset.exclude(interfaces__isnull=value)

    def _pass_through_ports(self, queryset, name, value):
        return queryset.exclude(
            frontports__isnull=value,
            rearports__isnull=value
        )


class DeviceComponentFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site__region',
        queryset=Region.objects.all(),
        label='Region (ID)',
    )
    region = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site__region__in',
        queryset=Region.objects.all(),
        label='Region name (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site__slug',
        queryset=Site.objects.all(),
        label='Site name (slug)',
    )
    device_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelMultipleChoiceFilter(
        field_name='device__name',
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )
    tag = TagFilter()

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        )


class ConsolePortFilterSet(DeviceComponentFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=ConsolePortTypeChoices,
        null_value=None
    )
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = ConsolePort
        fields = ['id', 'name', 'description', 'connection_status']


class ConsoleServerPortFilterSet(DeviceComponentFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=ConsolePortTypeChoices,
        null_value=None
    )
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = ConsoleServerPort
        fields = ['id', 'name', 'description', 'connection_status']


class PowerPortFilterSet(DeviceComponentFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=PowerPortTypeChoices,
        null_value=None
    )
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = PowerPort
        fields = ['id', 'name', 'maximum_draw', 'allocated_draw', 'description', 'connection_status']


class PowerOutletFilterSet(DeviceComponentFilterSet):
    type = django_filters.MultipleChoiceFilter(
        choices=PowerOutletTypeChoices,
        null_value=None
    )
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = PowerOutlet
        fields = ['id', 'name', 'feed_leg', 'description', 'connection_status']


class InterfaceFilterSet(django_filters.FilterSet):
    """
    Not using DeviceComponentFilterSet for Interfaces because we need to check for VirtualChassis membership.
    """
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site__region',
        queryset=Region.objects.all(),
        label='Region (ID)',
    )
    region = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site__region__in',
        queryset=Region.objects.all(),
        label='Region name (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site__slug',
        to_field_name='slug',
        queryset=Site.objects.all(),
        label='Site name (slug)',
    )
    device = MultiValueCharFilter(
        method='filter_device',
        field_name='name',
        label='Device',
    )
    device_id = MultiValueNumberFilter(
        method='filter_device_id',
        field_name='pk',
        label='Device (ID)',
    )
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )
    kind = django_filters.CharFilter(
        method='filter_kind',
        label='Kind of interface',
    )
    lag_id = django_filters.ModelMultipleChoiceFilter(
        field_name='lag',
        queryset=Interface.objects.all(),
        label='LAG interface (ID)',
    )
    mac_address = MultiValueMACAddressFilter()
    tag = TagFilter()
    vlan_id = django_filters.CharFilter(
        method='filter_vlan_id',
        label='Assigned VLAN'
    )
    vlan = django_filters.CharFilter(
        method='filter_vlan',
        label='Assigned VID'
    )
    type = django_filters.MultipleChoiceFilter(
        choices=InterfaceTypeChoices,
        null_value=None
    )

    class Meta:
        model = Interface
        fields = ['id', 'name', 'connection_status', 'type', 'enabled', 'mtu', 'mgmt_only', 'mode', 'description']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(name__icontains=value) |
            Q(description__icontains=value)
        ).distinct()

    def filter_device(self, queryset, name, value):
        try:
            devices = Device.objects.filter(**{'{}__in'.format(name): value})
            vc_interface_ids = []
            for device in devices:
                vc_interface_ids.extend(device.vc_interfaces.values_list('id', flat=True))
            return queryset.filter(pk__in=vc_interface_ids)
        except Device.DoesNotExist:
            return queryset.none()

    def filter_device_id(self, queryset, name, id_list):
        # Include interfaces belonging to peer virtual chassis members
        vc_interface_ids = []
        try:
            devices = Device.objects.filter(pk__in=id_list)
            for device in devices:
                vc_interface_ids += device.vc_interfaces.values_list('id', flat=True)
            return queryset.filter(pk__in=vc_interface_ids)
        except Device.DoesNotExist:
            return queryset.none()

    def filter_vlan_id(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        return queryset.filter(
            Q(untagged_vlan_id=value) |
            Q(tagged_vlans=value)
        )

    def filter_vlan(self, queryset, name, value):
        value = value.strip()
        if not value:
            return queryset
        return queryset.filter(
            Q(untagged_vlan_id__vid=value) |
            Q(tagged_vlans__vid=value)
        )

    def filter_kind(self, queryset, name, value):
        value = value.strip().lower()
        return {
            'physical': queryset.exclude(type__in=NONCONNECTABLE_IFACE_TYPES),
            'virtual': queryset.filter(type__in=VIRTUAL_IFACE_TYPES),
            'wireless': queryset.filter(type__in=WIRELESS_IFACE_TYPES),
        }.get(value, queryset.none())


class FrontPortFilterSet(DeviceComponentFilterSet):
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = FrontPort
        fields = ['id', 'name', 'type', 'description']


class RearPortFilterSet(DeviceComponentFilterSet):
    cabled = django_filters.BooleanFilter(
        field_name='cable',
        lookup_expr='isnull',
        exclude=True
    )

    class Meta:
        model = RearPort
        fields = ['id', 'name', 'type', 'positions', 'description']


class DeviceBayFilterSet(DeviceComponentFilterSet):

    class Meta:
        model = DeviceBay
        fields = ['id', 'name', 'description']


class InventoryItemFilterSet(DeviceComponentFilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='device__site__region__in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='device__site__region__in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='device__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site name (slug)',
    )
    device_id = django_filters.ModelChoiceFilter(
        queryset=Device.objects.all(),
        label='Device (ID)',
    )
    device = django_filters.ModelChoiceFilter(
        queryset=Device.objects.all(),
        to_field_name='name',
        label='Device (name)',
    )
    parent_id = django_filters.ModelMultipleChoiceFilter(
        queryset=InventoryItem.objects.all(),
        label='Parent inventory item (ID)',
    )
    manufacturer_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Manufacturer.objects.all(),
        label='Manufacturer (ID)',
    )
    manufacturer = django_filters.ModelMultipleChoiceFilter(
        field_name='manufacturer__slug',
        queryset=Manufacturer.objects.all(),
        to_field_name='slug',
        label='Manufacturer (slug)',
    )
    serial = django_filters.CharFilter(
        lookup_expr='iexact'
    )

    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'part_id', 'asset_tag', 'discovered']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(part_id__icontains=value) |
            Q(serial__icontains=value) |
            Q(asset_tag__icontains=value) |
            Q(description__icontains=value)
        )
        return queryset.filter(qs_filter)


class VirtualChassisFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='master__site__region__in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='master__site__region__in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='master__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='master__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site name (slug)',
    )
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        field_name='master__tenant',
        queryset=Tenant.objects.all(),
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        field_name='master__tenant__slug',
        queryset=Tenant.objects.all(),
        to_field_name='slug',
        label='Tenant (slug)',
    )
    tag = TagFilter()

    class Meta:
        model = VirtualChassis
        fields = ['id', 'domain']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(master__name__icontains=value) |
            Q(domain__icontains=value)
        )
        return queryset.filter(qs_filter)


class CableFilterSet(django_filters.FilterSet):
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    type = django_filters.MultipleChoiceFilter(
        choices=CableTypeChoices
    )
    status = django_filters.MultipleChoiceFilter(
        choices=CableStatusChoices
    )
    color = django_filters.MultipleChoiceFilter(
        choices=COLOR_CHOICES
    )
    device_id = MultiValueNumberFilter(
        method='filter_device'
    )
    device = MultiValueCharFilter(
        method='filter_device',
        field_name='device__name'
    )
    rack_id = MultiValueNumberFilter(
        method='filter_device',
        field_name='device__rack_id'
    )
    rack = MultiValueNumberFilter(
        method='filter_device',
        field_name='device__rack__name'
    )
    site_id = MultiValueNumberFilter(
        method='filter_device',
        field_name='device__site_id'
    )
    site = MultiValueNumberFilter(
        method='filter_device',
        field_name='device__site__slug'
    )

    class Meta:
        model = Cable
        fields = ['id', 'label', 'length', 'length_unit']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(label__icontains=value)

    def filter_device(self, queryset, name, value):
        queryset = queryset.filter(
            Q(**{'_termination_a_{}__in'.format(name): value}) |
            Q(**{'_termination_b_{}__in'.format(name): value})
        )
        return queryset


class ConsoleConnectionFilterSet(django_filters.FilterSet):
    site = django_filters.CharFilter(
        method='filter_site',
        label='Site (slug)',
    )
    device_id = MultiValueNumberFilter(
        method='filter_device'
    )
    device = MultiValueCharFilter(
        method='filter_device',
        field_name='device__name'
    )

    class Meta:
        model = ConsolePort
        fields = ['name', 'connection_status']

    def filter_site(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(connected_endpoint__device__site__slug=value)

    def filter_device(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(**{'{}__in'.format(name): value}) |
            Q(**{'connected_endpoint__{}__in'.format(name): value})
        )


class PowerConnectionFilterSet(django_filters.FilterSet):
    site = django_filters.CharFilter(
        method='filter_site',
        label='Site (slug)',
    )
    device_id = MultiValueNumberFilter(
        method='filter_device'
    )
    device = MultiValueCharFilter(
        method='filter_device',
        field_name='device__name'
    )

    class Meta:
        model = PowerPort
        fields = ['name', 'connection_status']

    def filter_site(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(_connected_poweroutlet__device__site__slug=value)

    def filter_device(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(**{'{}__in'.format(name): value}) |
            Q(**{'_connected_poweroutlet__{}__in'.format(name): value})
        )


class InterfaceConnectionFilterSet(django_filters.FilterSet):
    site = django_filters.CharFilter(
        method='filter_site',
        label='Site (slug)',
    )
    device_id = MultiValueNumberFilter(
        method='filter_device'
    )
    device = MultiValueCharFilter(
        method='filter_device',
        field_name='device__name'
    )

    class Meta:
        model = Interface
        fields = ['connection_status']

    def filter_site(self, queryset, name, value):
        if not value.strip():
            return queryset
        return queryset.filter(
            Q(device__site__slug=value) |
            Q(_connected_interface__device__site__slug=value)
        )

    def filter_device(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(**{'{}__in'.format(name): value}) |
            Q(**{'_connected_interface__{}__in'.format(name): value})
        )


class PowerPanelFilterSet(django_filters.FilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region__in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='site__region__in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site name (slug)',
    )
    rack_group_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack_group',
        queryset=RackGroup.objects.all(),
        label='Rack group (ID)',
    )

    class Meta:
        model = PowerPanel
        fields = ['name']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value)
        )
        return queryset.filter(qs_filter)


class PowerFeedFilterSet(CustomFieldFilterSet, CreatedUpdatedFilterSet):
    id__in = NumericInFilter(
        field_name='id',
        lookup_expr='in'
    )
    q = django_filters.CharFilter(
        method='search',
        label='Search',
    )
    region_id = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='power_panel__site__region__in',
        label='Region (ID)',
    )
    region = TreeNodeMultipleChoiceFilter(
        queryset=Region.objects.all(),
        field_name='power_panel__site__region__in',
        to_field_name='slug',
        label='Region (slug)',
    )
    site_id = django_filters.ModelMultipleChoiceFilter(
        field_name='power_panel__site',
        queryset=Site.objects.all(),
        label='Site (ID)',
    )
    site = django_filters.ModelMultipleChoiceFilter(
        field_name='power_panel__site__slug',
        queryset=Site.objects.all(),
        to_field_name='slug',
        label='Site name (slug)',
    )
    power_panel_id = django_filters.ModelMultipleChoiceFilter(
        queryset=PowerPanel.objects.all(),
        label='Power panel (ID)',
    )
    rack_id = django_filters.ModelMultipleChoiceFilter(
        field_name='rack',
        queryset=Rack.objects.all(),
        label='Rack (ID)',
    )
    tag = TagFilter()

    class Meta:
        model = PowerFeed
        fields = ['name', 'status', 'type', 'supply', 'phase', 'voltage', 'amperage', 'max_utilization']

    def search(self, queryset, name, value):
        if not value.strip():
            return queryset
        qs_filter = (
            Q(name__icontains=value) |
            Q(comments__icontains=value)
        )
        return queryset.filter(qs_filter)
