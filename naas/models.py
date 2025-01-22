from django.db import models
from nautobot.dcim.models import Location, DeviceType, Rack
from nautobot.ipam.models import VLAN, VRF, Prefix
from nautobot.extras.models import Tag
import uuid

class SiteOnboarding(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="sites")
    tags = models.ManyToManyField(Tag, related_name="siteonboardings", blank=True)
    num_prefixes_masks = models.PositiveIntegerField(default=0)
    vlans = models.ManyToManyField(VLAN, related_name="site_onboardings", blank=True)
    vlan_requirements = models.JSONField(blank=True, default=list)
    vlan_description = models.TextField(help_text="VLAN Description for the site onboarding.", blank=True, null=True)
    uplink = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Device(models.Model):
    site_onboarding = models.ForeignKey(SiteOnboarding, on_delete=models.CASCADE, related_name="devices")
    name = models.CharField(max_length=100)
    device_type = models.ForeignKey(DeviceType, on_delete=models.PROTECT)
    rack = models.ForeignKey(Rack, on_delete=models.PROTECT)
    vrfs = models.ManyToManyField(VRF, blank=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name