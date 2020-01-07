from django.contrib.auth.models import User
from django.test import TestCase

from dcim.constants import *
from dcim.filters import *
from dcim.models import (
    ConsolePortTemplate, ConsoleServerPortTemplate, DeviceBayTemplate, DeviceType, FrontPortTemplate, InterfaceTemplate,
    Manufacturer, PowerPortTemplate, PowerOutletTemplate, Rack, RackGroup, RackReservation, RackRole, RearPortTemplate,
    Region, Site,
)


class RegionTestCase(TestCase):
    queryset = Region.objects.all()

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        child_regions = (
            Region(name='Region 1A', slug='region-1a', parent=regions[0]),
            Region(name='Region 1B', slug='region-1b', parent=regions[0]),
            Region(name='Region 2A', slug='region-2a', parent=regions[1]),
            Region(name='Region 2B', slug='region-2b', parent=regions[1]),
            Region(name='Region 3A', slug='region-3a', parent=regions[2]),
            Region(name='Region 3B', slug='region-3b', parent=regions[2]),
        )
        for region in child_regions:
            region.save()

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(RegionFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Region 1', 'Region 2']}
        self.assertEqual(RegionFilter(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['region-1', 'region-2']}
        self.assertEqual(RegionFilter(params, self.queryset).qs.count(), 2)

    def test_parent(self):
        parent_regions = Region.objects.filter(parent__isnull=True)[:2]
        params = {'parent_id': [parent_regions[0].pk, parent_regions[1].pk]}
        self.assertEqual(RegionFilter(params, self.queryset).qs.count(), 4)
        params = {'parent': [parent_regions[0].slug, parent_regions[1].slug]}
        self.assertEqual(RegionFilter(params, self.queryset).qs.count(), 4)


class SiteTestCase(TestCase):
    queryset = Site.objects.all()

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0], status=SITE_STATUS_ACTIVE, facility='Facility 1', asn=65001, latitude=10, longitude=10, contact_name='Contact 1', contact_phone='123-555-0001', contact_email='contact1@example.com'),
            Site(name='Site 2', slug='site-2', region=regions[1], status=SITE_STATUS_PLANNED, facility='Facility 2', asn=65002, latitude=20, longitude=20, contact_name='Contact 2', contact_phone='123-555-0002', contact_email='contact2@example.com'),
            Site(name='Site 3', slug='site-3', region=regions[2], status=SITE_STATUS_RETIRED, facility='Facility 3', asn=65003, latitude=30, longitude=30, contact_name='Contact 3', contact_phone='123-555-0003', contact_email='contact3@example.com'),
        )
        Site.objects.bulk_create(sites)

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Site 1', 'Site 2']}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['site-1', 'site-2']}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_facility(self):
        params = {'facility': ['Facility 1', 'Facility 2']}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_asn(self):
        params = {'asn': [65001, 65002]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_latitude(self):
        params = {'latitude': [10, 20]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_longitude(self):
        params = {'longitude': [10, 20]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_contact_name(self):
        params = {'contact_name': ['Contact 1', 'Contact 2']}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_contact_phone(self):
        params = {'contact_phone': ['123-555-0001', '123-555-0002']}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_contact_email(self):
        params = {'contact_email': ['contact1@example.com', 'contact2@example.com']}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_id__in(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id__in': ','.join([str(id) for id in id_list])}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [SITE_STATUS_ACTIVE, SITE_STATUS_PLANNED]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(SiteFilter(params, self.queryset).qs.count(), 2)


class RackGroupTestCase(TestCase):
    queryset = RackGroup.objects.all()

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0]),
            Site(name='Site 2', slug='site-2', region=regions[1]),
            Site(name='Site 3', slug='site-3', region=regions[2]),
        )
        Site.objects.bulk_create(sites)

        rack_groups = (
            RackGroup(name='Rack Group 1', slug='rack-group-1', site=sites[0]),
            RackGroup(name='Rack Group 2', slug='rack-group-2', site=sites[1]),
            RackGroup(name='Rack Group 3', slug='rack-group-3', site=sites[2]),
        )
        RackGroup.objects.bulk_create(rack_groups)

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Rack Group 1', 'Rack Group 2']}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['rack-group-1', 'rack-group-2']}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(RackGroupFilter(params, self.queryset).qs.count(), 2)


class RackRoleTestCase(TestCase):
    queryset = RackRole.objects.all()

    @classmethod
    def setUpTestData(cls):

        rack_roles = (
            RackRole(name='Rack Role 1', slug='rack-role-1', color='ff0000'),
            RackRole(name='Rack Role 2', slug='rack-role-2', color='00ff00'),
            RackRole(name='Rack Role 3', slug='rack-role-3', color='0000ff'),
        )
        RackRole.objects.bulk_create(rack_roles)

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(RackRoleFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Rack Role 1', 'Rack Role 2']}
        self.assertEqual(RackRoleFilter(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['rack-role-1', 'rack-role-2']}
        self.assertEqual(RackRoleFilter(params, self.queryset).qs.count(), 2)

    def test_color(self):
        params = {'color': ['ff0000', '00ff00']}
        self.assertEqual(RackRoleFilter(params, self.queryset).qs.count(), 2)


class RackTestCase(TestCase):
    queryset = Rack.objects.all()

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Region 1', slug='region-1'),
            Region(name='Region 2', slug='region-2'),
            Region(name='Region 3', slug='region-3'),
        )
        for region in regions:
            region.save()

        sites = (
            Site(name='Site 1', slug='site-1', region=regions[0]),
            Site(name='Site 2', slug='site-2', region=regions[1]),
            Site(name='Site 3', slug='site-3', region=regions[2]),
        )
        Site.objects.bulk_create(sites)

        rack_groups = (
            RackGroup(name='Rack Group 1', slug='rack-group-1', site=sites[0]),
            RackGroup(name='Rack Group 2', slug='rack-group-2', site=sites[1]),
            RackGroup(name='Rack Group 3', slug='rack-group-3', site=sites[2]),
        )
        RackGroup.objects.bulk_create(rack_groups)

        rack_roles = (
            RackRole(name='Rack Role 1', slug='rack-role-1'),
            RackRole(name='Rack Role 2', slug='rack-role-2'),
            RackRole(name='Rack Role 3', slug='rack-role-3'),
        )
        RackRole.objects.bulk_create(rack_roles)

        racks = (
            Rack(name='Rack 1', facility_id='rack-1', site=sites[0], group=rack_groups[0], status=RACK_STATUS_ACTIVE, role=rack_roles[0], serial='ABC', asset_tag='1001', type=RACK_TYPE_2POST, width=RACK_WIDTH_19IN, u_height=42, desc_units=False, outer_width=100, outer_depth=100, outer_unit=LENGTH_UNIT_MILLIMETER),
            Rack(name='Rack 2', facility_id='rack-2', site=sites[1], group=rack_groups[1], status=RACK_STATUS_PLANNED, role=rack_roles[1], serial='DEF', asset_tag='1002', type=RACK_TYPE_4POST, width=RACK_WIDTH_19IN, u_height=43, desc_units=False, outer_width=200, outer_depth=200, outer_unit=LENGTH_UNIT_MILLIMETER),
            Rack(name='Rack 3', facility_id='rack-3', site=sites[2], group=rack_groups[2], status=RACK_STATUS_RESERVED, role=rack_roles[2], serial='GHI', asset_tag='1003', type=RACK_TYPE_CABINET, width=RACK_WIDTH_23IN, u_height=44, desc_units=True, outer_width=300, outer_depth=300, outer_unit=LENGTH_UNIT_INCH),
        )
        Rack.objects.bulk_create(racks)

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Rack 1', 'Rack 2']}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_facility_id(self):
        params = {'facility_id': ['rack-1', 'rack-2']}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_asset_tag(self):
        params = {'asset_tag': ['1001', '1002']}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_type(self):
        # TODO: Test for multiple values
        params = {'type': RACK_TYPE_2POST}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 1)

    def test_width(self):
        # TODO: Test for multiple values
        params = {'width': RACK_WIDTH_19IN}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_u_height(self):
        params = {'u_height': [42, 43]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_desc_units(self):
        params = {'desc_units': 'true'}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 1)
        params = {'desc_units': 'false'}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_outer_width(self):
        params = {'outer_width': [100, 200]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_outer_depth(self):
        params = {'outer_depth': [100, 200]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_outer_unit(self):
        self.assertEqual(Rack.objects.filter(outer_unit__isnull=False).count(), 3)
        params = {'outer_unit': LENGTH_UNIT_MILLIMETER}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_id__in(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id__in': ','.join([str(id) for id in id_list])}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_group(self):
        groups = RackGroup.objects.all()[:2]
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)
        params = {'group': [groups[0].slug, groups[1].slug]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {'status': [RACK_STATUS_ACTIVE, RACK_STATUS_PLANNED]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_role(self):
        roles = RackRole.objects.all()[:2]
        params = {'role_id': [roles[0].pk, roles[1].pk]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)
        params = {'role': [roles[0].slug, roles[1].slug]}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 2)

    def test_serial(self):
        params = {'serial': 'ABC'}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 1)
        params = {'serial': 'abc'}
        self.assertEqual(RackFilter(params, self.queryset).qs.count(), 1)


class RackReservationTestCase(TestCase):
    queryset = RackReservation.objects.all()

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Site 1', slug='site-1'),
            Site(name='Site 2', slug='site-2'),
            Site(name='Site 3', slug='site-3'),
        )
        Site.objects.bulk_create(sites)

        rack_groups = (
            RackGroup(name='Rack Group 1', slug='rack-group-1', site=sites[0]),
            RackGroup(name='Rack Group 2', slug='rack-group-2', site=sites[1]),
            RackGroup(name='Rack Group 3', slug='rack-group-3', site=sites[2]),
        )
        RackGroup.objects.bulk_create(rack_groups)

        racks = (
            Rack(name='Rack 1', site=sites[0], group=rack_groups[0]),
            Rack(name='Rack 2', site=sites[1], group=rack_groups[1]),
            Rack(name='Rack 3', site=sites[2], group=rack_groups[2]),
        )
        Rack.objects.bulk_create(racks)

        users = (
            User(username='User 1'),
            User(username='User 2'),
            User(username='User 3'),
        )
        User.objects.bulk_create(users)

        reservations = (
            RackReservation(rack=racks[0], units=[1, 2, 3], user=users[0]),
            RackReservation(rack=racks[1], units=[4, 5, 6], user=users[1]),
            RackReservation(rack=racks[2], units=[7, 8, 9], user=users[2]),
        )
        RackReservation.objects.bulk_create(reservations)

    def test_id__in(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id__in': ','.join([str(id) for id in id_list])}
        self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)

    def test_group(self):
        groups = RackGroup.objects.all()[:2]
        params = {'group_id': [groups[0].pk, groups[1].pk]}
        self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)
        params = {'group': [groups[0].slug, groups[1].slug]}
        self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)

    def test_user(self):
        users = User.objects.all()[:2]
        params = {'user_id': [users[0].pk, users[1].pk]}
        self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)
        # TODO: Filtering by username is broken
        # params = {'user': [users[0].username, users[1].username]}
        # self.assertEqual(RackReservationFilter(params, self.queryset).qs.count(), 2)


class ManufacturerTestCase(TestCase):
    queryset = Manufacturer.objects.all()

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(ManufacturerFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Manufacturer 1', 'Manufacturer 2']}
        self.assertEqual(ManufacturerFilter(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['manufacturer-1', 'manufacturer-2']}
        self.assertEqual(ManufacturerFilter(params, self.queryset).qs.count(), 2)


class DeviceTypeTestCase(TestCase):
    queryset = DeviceType.objects.all()

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer(name='Manufacturer 1', slug='manufacturer-1'),
            Manufacturer(name='Manufacturer 2', slug='manufacturer-2'),
            Manufacturer(name='Manufacturer 3', slug='manufacturer-3'),
        )
        Manufacturer.objects.bulk_create(manufacturers)

        device_types = (
            DeviceType(manufacturer=manufacturers[0], model='Model 1', slug='model-1', part_number='Part Number 1', u_height=1, is_full_depth=True, subdevice_role=None),
            DeviceType(manufacturer=manufacturers[1], model='Model 2', slug='model-2', part_number='Part Number 2', u_height=2, is_full_depth=True, subdevice_role=SUBDEVICE_ROLE_PARENT),
            DeviceType(manufacturer=manufacturers[2], model='Model 3', slug='model-3', part_number='Part Number 3', u_height=3, is_full_depth=False, subdevice_role=SUBDEVICE_ROLE_CHILD),
        )
        DeviceType.objects.bulk_create(device_types)

        # Add component templates for filtering
        ConsolePortTemplate.objects.bulk_create((
            ConsolePortTemplate(device_type=device_types[0], name='Console Port 1'),
            ConsolePortTemplate(device_type=device_types[1], name='Console Port 2'),
        ))
        ConsoleServerPortTemplate.objects.bulk_create((
            ConsoleServerPortTemplate(device_type=device_types[0], name='Console Server Port 1'),
            ConsoleServerPortTemplate(device_type=device_types[1], name='Console Server Port 2'),
        ))
        PowerPortTemplate.objects.bulk_create((
            PowerPortTemplate(device_type=device_types[0], name='Power Port 1'),
            PowerPortTemplate(device_type=device_types[1], name='Power Port 2'),
        ))
        PowerOutletTemplate.objects.bulk_create((
            PowerOutletTemplate(device_type=device_types[0], name='Power Outlet 1'),
            PowerOutletTemplate(device_type=device_types[1], name='Power Outlet 2'),
        ))
        InterfaceTemplate.objects.bulk_create((
            InterfaceTemplate(device_type=device_types[0], name='Interface 1'),
            InterfaceTemplate(device_type=device_types[1], name='Interface 2'),
        ))
        rear_ports = (
            RearPortTemplate(device_type=device_types[0], name='Rear Port 1', type=PORT_TYPE_8P8C),
            RearPortTemplate(device_type=device_types[1], name='Rear Port 2', type=PORT_TYPE_8P8C),
        )
        RearPortTemplate.objects.bulk_create(rear_ports)
        FrontPortTemplate.objects.bulk_create((
            FrontPortTemplate(device_type=device_types[0], name='Front Port 1', type=PORT_TYPE_8P8C, rear_port=rear_ports[0]),
            FrontPortTemplate(device_type=device_types[1], name='Front Port 2', type=PORT_TYPE_8P8C, rear_port=rear_ports[1]),
        ))
        DeviceBayTemplate.objects.bulk_create((
            DeviceBayTemplate(device_type=device_types[0], name='Device Bay 1'),
            DeviceBayTemplate(device_type=device_types[1], name='Device Bay 2'),
        ))

    def test_model(self):
        params = {'model': ['Model 1', 'Model 2']}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['model-1', 'model-2']}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)

    def test_part_number(self):
        params = {'part_number': ['Part Number 1', 'Part Number 2']}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)

    def test_u_height(self):
        params = {'u_height': [1, 2]}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)

    def test_is_full_depth(self):
        params = {'is_full_depth': 'true'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)
        params = {'is_full_depth': 'false'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 1)

    def test_subdevice_role(self):
        params = {'subdevice_role': SUBDEVICE_ROLE_PARENT}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 1)

    def test_id__in(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id__in': ','.join([str(id) for id in id_list])}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {'manufacturer_id': [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)
        params = {'manufacturer': [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)

    def test_console_ports(self):
        params = {'console_ports': 'true'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)
        params = {'console_ports': 'false'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 1)

    def test_console_server_ports(self):
        params = {'console_server_ports': 'true'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)
        params = {'console_server_ports': 'false'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 1)

    def test_power_ports(self):
        params = {'power_ports': 'true'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)
        params = {'power_ports': 'false'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 1)

    def test_power_outlets(self):
        params = {'power_outlets': 'true'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)
        params = {'power_outlets': 'false'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 1)

    def test_interfaces(self):
        params = {'interfaces': 'true'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)
        params = {'interfaces': 'false'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 1)

    def test_pass_through_ports(self):
        params = {'pass_through_ports': 'true'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)
        params = {'pass_through_ports': 'false'}
        self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 1)

    # TODO: Add device_bay filter
    # def test_device_bays(self):
    #     params = {'device_bays': 'true'}
    #     self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 2)
    #     params = {'device_bays': 'false'}
    #     self.assertEqual(DeviceTypeFilter(params, self.queryset).qs.count(), 1)


class ConsolePortTemplateTestCase(TestCase):
    queryset = ConsolePortTemplate.objects.all()

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        ConsolePortTemplate.objects.bulk_create((
            ConsolePortTemplate(device_type=device_types[0], name='Console Port 1'),
            ConsolePortTemplate(device_type=device_types[1], name='Console Port 2'),
            ConsolePortTemplate(device_type=device_types[2], name='Console Port 3'),
        ))

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(ConsolePortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Console Port 1', 'Console Port 2']}
        self.assertEqual(ConsolePortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'devicetype_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(ConsolePortTemplateFilter(params, self.queryset).qs.count(), 2)


class ConsoleServerPortTemplateTestCase(TestCase):
    queryset = ConsoleServerPortTemplate.objects.all()

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        ConsoleServerPortTemplate.objects.bulk_create((
            ConsoleServerPortTemplate(device_type=device_types[0], name='Console Server Port 1'),
            ConsoleServerPortTemplate(device_type=device_types[1], name='Console Server Port 2'),
            ConsoleServerPortTemplate(device_type=device_types[2], name='Console Server Port 3'),
        ))

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(ConsoleServerPortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Console Server Port 1', 'Console Server Port 2']}
        self.assertEqual(ConsoleServerPortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'devicetype_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(ConsoleServerPortTemplateFilter(params, self.queryset).qs.count(), 2)


class PowerPortTemplateTestCase(TestCase):
    queryset = PowerPortTemplate.objects.all()

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        PowerPortTemplate.objects.bulk_create((
            PowerPortTemplate(device_type=device_types[0], name='Power Port 1', maximum_draw=100, allocated_draw=50),
            PowerPortTemplate(device_type=device_types[1], name='Power Port 2', maximum_draw=200, allocated_draw=100),
            PowerPortTemplate(device_type=device_types[2], name='Power Port 3', maximum_draw=300, allocated_draw=150),
        ))

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(PowerPortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Power Port 1', 'Power Port 2']}
        self.assertEqual(PowerPortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'devicetype_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(PowerPortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_maximum_draw(self):
        params = {'maximum_draw': [100, 200]}
        self.assertEqual(PowerPortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_allocated_draw(self):
        params = {'allocated_draw': [50, 100]}
        self.assertEqual(PowerPortTemplateFilter(params, self.queryset).qs.count(), 2)


class PowerOutletTemplateTestCase(TestCase):
    queryset = PowerOutletTemplate.objects.all()

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        PowerOutletTemplate.objects.bulk_create((
            PowerOutletTemplate(device_type=device_types[0], name='Power Outlet 1', feed_leg=POWERFEED_LEG_A),
            PowerOutletTemplate(device_type=device_types[1], name='Power Outlet 2', feed_leg=POWERFEED_LEG_B),
            PowerOutletTemplate(device_type=device_types[2], name='Power Outlet 3', feed_leg=POWERFEED_LEG_C),
        ))

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(PowerOutletTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Power Outlet 1', 'Power Outlet 2']}
        self.assertEqual(PowerOutletTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'devicetype_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(PowerOutletTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_feed_leg(self):
        # TODO: Support filtering for multiple values
        params = {'feed_leg': POWERFEED_LEG_A}
        self.assertEqual(PowerOutletTemplateFilter(params, self.queryset).qs.count(), 1)


class InterfaceTemplateTestCase(TestCase):
    queryset = InterfaceTemplate.objects.all()

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        InterfaceTemplate.objects.bulk_create((
            InterfaceTemplate(device_type=device_types[0], name='Interface 1', type=IFACE_TYPE_1GE_FIXED, mgmt_only=True),
            InterfaceTemplate(device_type=device_types[1], name='Interface 2', type=IFACE_TYPE_1GE_GBIC, mgmt_only=False),
            InterfaceTemplate(device_type=device_types[2], name='Interface 3', type=IFACE_TYPE_1GE_SFP, mgmt_only=False),
        ))

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(InterfaceTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Interface 1', 'Interface 2']}
        self.assertEqual(InterfaceTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'devicetype_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(InterfaceTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_type(self):
        # TODO: Support filtering for multiple values
        params = {'type': IFACE_TYPE_1GE_FIXED}
        self.assertEqual(InterfaceTemplateFilter(params, self.queryset).qs.count(), 1)

    def test_mgmt_only(self):
        params = {'mgmt_only': 'true'}
        self.assertEqual(InterfaceTemplateFilter(params, self.queryset).qs.count(), 1)
        params = {'mgmt_only': 'false'}
        self.assertEqual(InterfaceTemplateFilter(params, self.queryset).qs.count(), 2)


class FrontPortTemplateTestCase(TestCase):
    queryset = FrontPortTemplate.objects.all()

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        rear_ports = (
            RearPortTemplate(device_type=device_types[0], name='Rear Port 1', type=PORT_TYPE_8P8C),
            RearPortTemplate(device_type=device_types[1], name='Rear Port 2', type=PORT_TYPE_8P8C),
            RearPortTemplate(device_type=device_types[2], name='Rear Port 3', type=PORT_TYPE_8P8C),
        )
        RearPortTemplate.objects.bulk_create(rear_ports)

        FrontPortTemplate.objects.bulk_create((
            FrontPortTemplate(device_type=device_types[0], name='Front Port 1', rear_port=rear_ports[0], type=PORT_TYPE_8P8C),
            FrontPortTemplate(device_type=device_types[1], name='Front Port 2', rear_port=rear_ports[1], type=PORT_TYPE_110_PUNCH),
            FrontPortTemplate(device_type=device_types[2], name='Front Port 3', rear_port=rear_ports[2], type=PORT_TYPE_BNC),
        ))

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(FrontPortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Front Port 1', 'Front Port 2']}
        self.assertEqual(FrontPortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'devicetype_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(FrontPortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_type(self):
        # TODO: Support filtering for multiple values
        params = {'type': PORT_TYPE_8P8C}
        self.assertEqual(FrontPortTemplateFilter(params, self.queryset).qs.count(), 1)


class RearPortTemplateTestCase(TestCase):
    queryset = RearPortTemplate.objects.all()

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        RearPortTemplate.objects.bulk_create((
            RearPortTemplate(device_type=device_types[0], name='Rear Port 1', type=PORT_TYPE_8P8C, positions=1),
            RearPortTemplate(device_type=device_types[1], name='Rear Port 2', type=PORT_TYPE_110_PUNCH, positions=2),
            RearPortTemplate(device_type=device_types[2], name='Rear Port 3', type=PORT_TYPE_BNC, positions=3),
        ))

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(RearPortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Rear Port 1', 'Rear Port 2']}
        self.assertEqual(RearPortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'devicetype_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(RearPortTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_type(self):
        # TODO: Support filtering for multiple values
        params = {'type': PORT_TYPE_8P8C}
        self.assertEqual(RearPortTemplateFilter(params, self.queryset).qs.count(), 1)

    def test_positions(self):
        params = {'positions': [1, 2]}
        self.assertEqual(RearPortTemplateFilter(params, self.queryset).qs.count(), 2)


class DeviceBayTemplateTestCase(TestCase):
    queryset = DeviceBayTemplate.objects.all()

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name='Manufacturer 1', slug='manufacturer-1')

        device_types = (
            DeviceType(manufacturer=manufacturer, model='Model 1', slug='model-1'),
            DeviceType(manufacturer=manufacturer, model='Model 2', slug='model-2'),
            DeviceType(manufacturer=manufacturer, model='Model 3', slug='model-3'),
        )
        DeviceType.objects.bulk_create(device_types)

        DeviceBayTemplate.objects.bulk_create((
            DeviceBayTemplate(device_type=device_types[0], name='Device Bay 1'),
            DeviceBayTemplate(device_type=device_types[1], name='Device Bay 2'),
            DeviceBayTemplate(device_type=device_types[2], name='Device Bay 3'),
        ))

    def test_id(self):
        id_list = self.queryset.values_list('id', flat=True)[:2]
        params = {'id': [str(id) for id in id_list]}
        self.assertEqual(DeviceBayTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {'name': ['Device Bay 1', 'Device Bay 2']}
        self.assertEqual(DeviceBayTemplateFilter(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {'devicetype_id': [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(DeviceBayTemplateFilter(params, self.queryset).qs.count(), 2)
