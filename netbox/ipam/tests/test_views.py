from netaddr import IPNetwork
import urllib.parse

from django.urls import reverse

from dcim.models import Device, DeviceRole, DeviceType, Manufacturer, Site
from ipam.choices import ServiceProtocolChoices
from ipam.models import Aggregate, IPAddress, Prefix, RIR, Role, Service, VLAN, VLANGroup, VRF
from utilities.testing import TestCase


class VRFTestCase(TestCase):
    user_permissions = (
        'ipam.view_vrf',
    )

    @classmethod
    def setUpTestData(cls):

        VRF.objects.bulk_create([
            VRF(name='VRF 1', rd='65000:1'),
            VRF(name='VRF 2', rd='65000:2'),
            VRF(name='VRF 3', rd='65000:3'),
        ])

    def test_vrf_list(self):

        url = reverse('ipam:vrf_list')
        params = {
            "q": "65000",
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertHttpStatus(response, 200)

    def test_vrf(self):

        vrf = VRF.objects.first()
        response = self.client.get(vrf.get_absolute_url())
        self.assertHttpStatus(response, 200)

    def test_vrf_import(self):
        self.add_permissions('ipam.add_vrf')

        csv_data = (
            "name",
            "VRF 4",
            "VRF 5",
            "VRF 6",
        )

        response = self.client.post(reverse('ipam:vrf_import'), {'csv': '\n'.join(csv_data)})

        self.assertHttpStatus(response, 200)
        self.assertEqual(VRF.objects.count(), 6)


class RIRTestCase(TestCase):
    user_permissions = (
        'ipam.view_rir',
    )

    @classmethod
    def setUpTestData(cls):

        RIR.objects.bulk_create([
            RIR(name='RIR 1', slug='rir-1'),
            RIR(name='RIR 2', slug='rir-2'),
            RIR(name='RIR 3', slug='rir-3'),
        ])

    def test_rir_list(self):

        url = reverse('ipam:rir_list')

        response = self.client.get(url)
        self.assertHttpStatus(response, 200)

    def test_rir_import(self):
        self.add_permissions('ipam.add_rir')

        csv_data = (
            "name,slug",
            "RIR 4,rir-4",
            "RIR 5,rir-5",
            "RIR 6,rir-6",
        )

        response = self.client.post(reverse('ipam:rir_import'), {'csv': '\n'.join(csv_data)})

        self.assertHttpStatus(response, 200)
        self.assertEqual(RIR.objects.count(), 6)


class AggregateTestCase(TestCase):
    user_permissions = (
        'ipam.view_aggregate',
    )

    @classmethod
    def setUpTestData(cls):

        rir = RIR(name='RIR 1', slug='rir-1')
        rir.save()

        Aggregate.objects.bulk_create([
            Aggregate(family=4, prefix=IPNetwork('10.1.0.0/16'), rir=rir),
            Aggregate(family=4, prefix=IPNetwork('10.2.0.0/16'), rir=rir),
            Aggregate(family=4, prefix=IPNetwork('10.3.0.0/16'), rir=rir),
        ])

    def test_aggregate_list(self):

        url = reverse('ipam:aggregate_list')
        params = {
            "rir": RIR.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertHttpStatus(response, 200)

    def test_aggregate(self):

        aggregate = Aggregate.objects.first()
        response = self.client.get(aggregate.get_absolute_url())
        self.assertHttpStatus(response, 200)

    def test_aggregate_import(self):
        self.add_permissions('ipam.add_aggregate')

        csv_data = (
            "prefix,rir",
            "10.4.0.0/16,RIR 1",
            "10.5.0.0/16,RIR 1",
            "10.6.0.0/16,RIR 1",
        )

        response = self.client.post(reverse('ipam:aggregate_import'), {'csv': '\n'.join(csv_data)})

        self.assertHttpStatus(response, 200)
        self.assertEqual(Aggregate.objects.count(), 6)


class RoleTestCase(TestCase):
    user_permissions = (
        'ipam.view_role',
    )

    @classmethod
    def setUpTestData(cls):

        Role.objects.bulk_create([
            Role(name='Role 1', slug='role-1'),
            Role(name='Role 2', slug='role-2'),
            Role(name='Role 3', slug='role-3'),
        ])

    def test_role_list(self):

        url = reverse('ipam:role_list')

        response = self.client.get(url)
        self.assertHttpStatus(response, 200)

    def test_role_import(self):
        self.add_permissions('ipam.add_role')

        csv_data = (
            "name,slug,weight",
            "Role 4,role-4,1000",
            "Role 5,role-5,1000",
            "Role 6,role-6,1000",
        )

        response = self.client.post(reverse('ipam:role_import'), {'csv': '\n'.join(csv_data)})

        self.assertHttpStatus(response, 200)
        self.assertEqual(Role.objects.count(), 6)


class PrefixTestCase(TestCase):
    user_permissions = (
        'ipam.view_prefix',
    )

    @classmethod
    def setUpTestData(cls):

        site = Site(name='Site 1', slug='site-1')
        site.save()

        Prefix.objects.bulk_create([
            Prefix(family=4, prefix=IPNetwork('10.1.0.0/16'), site=site),
            Prefix(family=4, prefix=IPNetwork('10.2.0.0/16'), site=site),
            Prefix(family=4, prefix=IPNetwork('10.3.0.0/16'), site=site),
        ])

    def test_prefix_list(self):

        url = reverse('ipam:prefix_list')
        params = {
            "site": Site.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertHttpStatus(response, 200)

    def test_prefix(self):

        prefix = Prefix.objects.first()
        response = self.client.get(prefix.get_absolute_url())
        self.assertHttpStatus(response, 200)

    def test_prefix_import(self):
        self.add_permissions('ipam.add_prefix')

        csv_data = (
            "prefix,status",
            "10.4.0.0/16,Active",
            "10.5.0.0/16,Active",
            "10.6.0.0/16,Active",
        )

        response = self.client.post(reverse('ipam:prefix_import'), {'csv': '\n'.join(csv_data)})

        self.assertHttpStatus(response, 200)
        self.assertEqual(Prefix.objects.count(), 6)


class IPAddressTestCase(TestCase):
    user_permissions = (
        'ipam.view_ipaddress',
    )

    @classmethod
    def setUpTestData(cls):

        vrf = VRF(name='VRF 1', rd='65000:1')
        vrf.save()

        IPAddress.objects.bulk_create([
            IPAddress(family=4, address=IPNetwork('192.0.2.1/24'), vrf=vrf),
            IPAddress(family=4, address=IPNetwork('192.0.2.2/24'), vrf=vrf),
            IPAddress(family=4, address=IPNetwork('192.0.2.3/24'), vrf=vrf),
        ])

    def test_ipaddress_list(self):

        url = reverse('ipam:ipaddress_list')
        params = {
            "vrf": VRF.objects.first().rd,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertHttpStatus(response, 200)

    def test_ipaddress(self):

        ipaddress = IPAddress.objects.first()
        response = self.client.get(ipaddress.get_absolute_url())
        self.assertHttpStatus(response, 200)

    def test_ipaddress_import(self):
        self.add_permissions('ipam.add_ipaddress')

        csv_data = (
            "address,status",
            "192.0.2.4/24,Active",
            "192.0.2.5/24,Active",
            "192.0.2.6/24,Active",
        )

        response = self.client.post(reverse('ipam:ipaddress_import'), {'csv': '\n'.join(csv_data)})

        self.assertHttpStatus(response, 200)
        self.assertEqual(IPAddress.objects.count(), 6)


class VLANGroupTestCase(TestCase):
    user_permissions = (
        'ipam.view_vlangroup',
    )

    @classmethod
    def setUpTestData(cls):

        site = Site(name='Site 1', slug='site-1')
        site.save()

        VLANGroup.objects.bulk_create([
            VLANGroup(name='VLAN Group 1', slug='vlan-group-1', site=site),
            VLANGroup(name='VLAN Group 2', slug='vlan-group-2', site=site),
            VLANGroup(name='VLAN Group 3', slug='vlan-group-3', site=site),
        ])

    def test_vlangroup_list(self):

        url = reverse('ipam:vlangroup_list')
        params = {
            "site": Site.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertHttpStatus(response, 200)

    def test_vlangroup_import(self):
        self.add_permissions('ipam.add_vlangroup')

        csv_data = (
            "name,slug",
            "VLAN Group 4,vlan-group-4",
            "VLAN Group 5,vlan-group-5",
            "VLAN Group 6,vlan-group-6",
        )

        response = self.client.post(reverse('ipam:vlangroup_import'), {'csv': '\n'.join(csv_data)})

        self.assertHttpStatus(response, 200)
        self.assertEqual(VLANGroup.objects.count(), 6)


class VLANTestCase(TestCase):
    user_permissions = (
        'ipam.view_vlan',
    )

    @classmethod
    def setUpTestData(cls):

        vlangroup = VLANGroup(name='VLAN Group 1', slug='vlan-group-1')
        vlangroup.save()

        VLAN.objects.bulk_create([
            VLAN(group=vlangroup, vid=101, name='VLAN101'),
            VLAN(group=vlangroup, vid=102, name='VLAN102'),
            VLAN(group=vlangroup, vid=103, name='VLAN103'),
        ])

    def test_vlan_list(self):

        url = reverse('ipam:vlan_list')
        params = {
            "group": VLANGroup.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertHttpStatus(response, 200)

    def test_vlan(self):

        vlan = VLAN.objects.first()
        response = self.client.get(vlan.get_absolute_url())
        self.assertHttpStatus(response, 200)

    def test_vlan_import(self):
        self.add_permissions('ipam.add_vlan')

        csv_data = (
            "vid,name,status",
            "104,VLAN104,Active",
            "105,VLAN105,Active",
            "106,VLAN106,Active",
        )

        response = self.client.post(reverse('ipam:vlan_import'), {'csv': '\n'.join(csv_data)})

        self.assertHttpStatus(response, 200)
        self.assertEqual(VLAN.objects.count(), 6)


class ServiceTestCase(TestCase):
    user_permissions = (
        'ipam.view_service',
    )

    @classmethod
    def setUpTestData(cls):

        site = Site(name='Site 1', slug='site-1')
        site.save()

        manufacturer = Manufacturer(name='Manufacturer 1', slug='manufacturer-1')
        manufacturer.save()

        devicetype = DeviceType(manufacturer=manufacturer, model='Device Type 1')
        devicetype.save()

        devicerole = DeviceRole(name='Device Role 1', slug='device-role-1')
        devicerole.save()

        device = Device(name='Device 1', site=site, device_type=devicetype, device_role=devicerole)
        device.save()

        Service.objects.bulk_create([
            Service(device=device, name='Service 1', protocol=ServiceProtocolChoices.PROTOCOL_TCP, port=101),
            Service(device=device, name='Service 2', protocol=ServiceProtocolChoices.PROTOCOL_TCP, port=102),
            Service(device=device, name='Service 3', protocol=ServiceProtocolChoices.PROTOCOL_TCP, port=103),
        ])

    def test_service_list(self):

        url = reverse('ipam:service_list')
        params = {
            "device_id": Device.objects.first(),
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertHttpStatus(response, 200)

    def test_service(self):

        service = Service.objects.first()
        response = self.client.get(service.get_absolute_url())
        self.assertHttpStatus(response, 200)
