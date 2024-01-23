from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.signals import m2m_changed, pre_delete, pre_save
from django.dispatch import receiver

from nautobot.ipam.models import IPAddressToInterface, VLAN, VRF, VRFDeviceAssignment, VRFPrefixAssignment


@receiver(pre_save, sender=VRFDeviceAssignment)
@receiver(pre_save, sender=VRFPrefixAssignment)
def ipam_object_saved(sender, instance, raw=False, **kwargs):
    """
    Forcibly call `full_clean()` when a new IPAM intermediate model is manually saved to prevent
    creation of invalid objects.
    """
    if raw:
        return
    instance.full_clean()


@receiver(m2m_changed, sender=VRFPrefixAssignment)
def vrf_prefix_associated(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Disallow adding Prefixes if the namespace doesn't match.
    """

    if action == "pre_add":
        prefixes = model.objects.filter(pk__in=pk_set).exclude(namespace=instance.namespace)
        if prefixes.exists():
            raise ValidationError({"prefixes": "Prefix must match namespace of VRF"})


@receiver(m2m_changed, sender=VRFDeviceAssignment)
def vrf_device_associated(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Assert validation on m2m when devices are associated with a VRF.
    """

    # TODO(jathan): Temporary workaround until a formset to add/remove/update VRFs <-> Devices and
    # optionally setting RD/name on assignment. k
    if action == "post_add":
        if isinstance(instance, VRF):
            for assignment in instance.device_assignments.iterator():
                assignment.validated_save()
        else:
            for assignment in instance.vrf_assignments.iterator():
                assignment.validated_save()


@receiver(pre_delete, sender=IPAddressToInterface)
def ip_address_to_interface_pre_delete(instance, raw=False, **kwargs):
    if raw:
        return

    # Check if the removed IPAddressToInterface instance contains an IPAddress
    # that is the primary_v{version} of the host machine.

    if getattr(instance, "interface"):
        host = instance.interface.device
        other_assignments_exist = (
            IPAddressToInterface.objects.filter(interface__device=host, ip_address=instance.ip_address)
            .exclude(id=instance.id)
            .exists()
        )
    else:
        host = instance.vm_interface.virtual_machine
        other_assignments_exist = (
            IPAddressToInterface.objects.filter(vm_interface__virtual_machine=host, ip_address=instance.ip_address)
            .exclude(id=instance.id)
            .exists()
        )

    # Only nullify the primary_ip field if no other interfaces/vm_interfaces have the ip_address
    if not other_assignments_exist and instance.ip_address == host.primary_ip4:
        host.primary_ip4 = None
    elif not other_assignments_exist and instance.ip_address == host.primary_ip6:
        host.primary_ip6 = None
    host.save()


@receiver(pre_save, sender=IPAddressToInterface)
def ip_address_to_interface_assignment_created(sender, instance, raw=False, **kwargs):
    """
    Forcibly call `full_clean()` when a new `IPAddressToInterface` object
    is manually created to prevent inadvertantly creating invalid IPAddressToInterface.
    """
    if raw:
        return

    instance.full_clean()


@receiver(m2m_changed, sender=VLAN.locations.through)
def assert_vlan_locations_content_types(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "pre_add":
        instance_ct = ContentType.objects.get_for_model(instance)
        invalid_locations = model.objects.select_related("location_type").filter(
            Q(pk__in=pk_set), ~Q(location_type__content_types__in=[instance_ct])
        )
        if invalid_locations.exists():
            invalid_location_types = {location.location_type.name for location in invalid_locations}
            raise ValidationError(
                {"locations": f"VLANs may not associate to locations of types {list(invalid_location_types)}."}
            )
