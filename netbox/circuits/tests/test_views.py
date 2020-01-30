import urllib.parse

from django.urls import reverse

from circuits.models import Circuit, CircuitType, Provider
from utilities.testing import TestCase


class ProviderTestCase(TestCase):
    user_permissions = (
        'circuits.view_provider',
    )

    @classmethod
    def setUpTestData(cls):
        Provider.objects.bulk_create([
            Provider(name='Provider 1', slug='provider-1', asn=65001),
            Provider(name='Provider 2', slug='provider-2', asn=65002),
            Provider(name='Provider 3', slug='provider-3', asn=65003),
        ])

    def test_provider_list(self):
        url = reverse('circuits:provider_list')
        params = {
            "q": "test",
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertHttpStatus(response, 200)

    def test_provider(self):
        provider = Provider.objects.first()
        response = self.client.get(provider.get_absolute_url())
        self.assertHttpStatus(response, 200)

    def test_provider_import(self):
        self.add_permissions('circuits.add_provider')
        csv_data = (
            "name,slug",
            "Provider 4,provider-4",
            "Provider 5,provider-5",
            "Provider 6,provider-6",
        )

        response = self.client.post(reverse('circuits:provider_import'), {'csv': '\n'.join(csv_data)})

        self.assertHttpStatus(response, 200)
        self.assertEqual(Provider.objects.count(), 6)


class CircuitTypeTestCase(TestCase):
    user_permissions = (
        'circuits.view_circuittype',
    )

    @classmethod
    def setUpTestData(cls):

        CircuitType.objects.bulk_create([
            CircuitType(name='Circuit Type 1', slug='circuit-type-1'),
            CircuitType(name='Circuit Type 2', slug='circuit-type-2'),
            CircuitType(name='Circuit Type 3', slug='circuit-type-3'),
        ])

    def test_circuittype_list(self):

        url = reverse('circuits:circuittype_list')

        response = self.client.get(url)
        self.assertHttpStatus(response, 200)

    def test_circuittype_import(self):
        self.add_permissions('circuits.add_circuittype')

        csv_data = (
            "name,slug",
            "Circuit Type 4,circuit-type-4",
            "Circuit Type 5,circuit-type-5",
            "Circuit Type 6,circuit-type-6",
        )

        response = self.client.post(reverse('circuits:circuittype_import'), {'csv': '\n'.join(csv_data)})

        self.assertHttpStatus(response, 200)
        self.assertEqual(CircuitType.objects.count(), 6)


class CircuitTestCase(TestCase):
    user_permissions = (
        'circuits.view_circuit',
    )

    @classmethod
    def setUpTestData(cls):

        provider = Provider(name='Provider 1', slug='provider-1', asn=65001)
        provider.save()

        circuittype = CircuitType(name='Circuit Type 1', slug='circuit-type-1')
        circuittype.save()

        Circuit.objects.bulk_create([
            Circuit(cid='Circuit 1', provider=provider, type=circuittype),
            Circuit(cid='Circuit 2', provider=provider, type=circuittype),
            Circuit(cid='Circuit 3', provider=provider, type=circuittype),
        ])

    def test_circuit_list(self):

        url = reverse('circuits:circuit_list')
        params = {
            "provider": Provider.objects.first().slug,
            "type": CircuitType.objects.first().slug,
        }

        response = self.client.get('{}?{}'.format(url, urllib.parse.urlencode(params)))
        self.assertHttpStatus(response, 200)

    def test_circuit(self):

        circuit = Circuit.objects.first()
        response = self.client.get(circuit.get_absolute_url())
        self.assertHttpStatus(response, 200)

    def test_circuit_import(self):
        self.add_permissions('circuits.add_circuit')

        csv_data = (
            "cid,provider,type",
            "Circuit 4,Provider 1,Circuit Type 1",
            "Circuit 5,Provider 1,Circuit Type 1",
            "Circuit 6,Provider 1,Circuit Type 1",
        )

        response = self.client.post(reverse('circuits:circuit_import'), {'csv': '\n'.join(csv_data)})

        self.assertHttpStatus(response, 200)
        self.assertEqual(Circuit.objects.count(), 6)
