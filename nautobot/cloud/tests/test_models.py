from django.core.exceptions import ValidationError

from nautobot.cloud import models
from nautobot.core.testing.models import ModelTestCases


class CloudAccountModelTestCase(ModelTestCases.BaseModelTestCase):
    model = models.CloudAccount


class CloudTypeModelTestCase(ModelTestCases.BaseModelTestCase):
    model = models.CloudType


class CloudNetworkModelTestCase(ModelTestCases.BaseModelTestCase):
    model = models.CloudNetwork

    def test_parent_may_not_have_parent(self):
        illegal_parent = models.CloudNetwork.objects.filter(parent__isnull=False).first()
        with self.assertRaises(ValidationError):
            models.CloudNetwork(
                name="Grandchild",
                cloud_account=models.CloudAccount.objects.first(),
                cloud_type=models.CloudType.objects.first(),
                parent=illegal_parent,
            ).clean()

    def test_parent_may_not_be_self(self):
        cloud_network = models.CloudNetwork(
            name="Loop",
            cloud_account=models.CloudAccount.objects.last(),
            cloud_type=models.CloudType.objects.last(),
        )
        cloud_network.validated_save()
        with self.assertRaises(ValidationError):
            cloud_network.parent = cloud_network
            cloud_network.clean()

    # TODO: test schema validation of extra_config


class CloudNetworkPrefixAssignmentModelTestCase(ModelTestCases.BaseModelTestCase):
    model = models.CloudNetworkPrefixAssignment
