import uuid
from django.db import models
from nautobot.core.models import BaseModel
from nautobot.dcim.models import Location, DeviceType, Rack
from nautobot.ipam.models import VLAN, Prefix, VRF
from nautobot.extras.models import Tag
from nautobot.core.constants import CHARFIELD_MAX_LENGTH

class SiteOnboarding(BaseModel):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, unique=True)
    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH)
    location = models.ForeignKey(
        to=Location,  
        on_delete=models.PROTECT,
        related_name="sites",
        help_text="The location where the site is situated."
    )
    site_tag = models.CharField(max_length=CHARFIELD_MAX_LENGTH)
    device_type = models.ForeignKey(
        to=DeviceType,  
        on_delete=models.CASCADE,
        related_name="site_onboardings",
        help_text="The type of device associated with the site."
    )
    tags = models.ManyToManyField(
        to=Tag,  # Reference to Tag model for the many-to-many relationship
        related_name="siteonboardings",
        blank=True,
        help_text="Tags associated with the site for categorization."
    )
    device_number = models.PositiveIntegerField()
    num_prefixes_masks = models.PositiveIntegerField(default=0)
    racks = models.ManyToManyField(
        to=Rack,
        related_name="site_onboardings",
        help_text="The racks associated with the site."
    )
    vlans = models.ManyToManyField(
        to=VLAN,
        related_name="site_onboardings",
        help_text="The VLANs associated with the site."
    )
    prefixes = models.ManyToManyField(
        to=Prefix,
        related_name="site_onboardings",
        help_text="The prefixes associated with the site."
    )
    vrfs = models.ManyToManyField(
        to=VRF,
        related_name="site_onboardings",
        help_text="The VRFs associated with the site."
    )
    uplink = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH,
        help_text="The uplink information for the site.",
        blank=True,
        null=True
    )
    vlan_description = models.TextField(
        help_text="VLAN Description for the site onboarding.",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Site Onboarding"
        verbose_name_plural = "Site Onboardings"

class SiteOnboardingTag(models.Model):
    site_onboarding = models.ForeignKey(
        "SiteOnboarding", 
        on_delete=models.CASCADE, 
        related_name="siteonboarding_tags", 
        to_field='id'  # Explicitly set to reference UUID field `id`
    )
