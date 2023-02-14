import uuid

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from nautobot.core.utils.color import hex_to_rgb, lighten_color, rgb_to_hex
from nautobot.dcim.choices import InterfaceModeChoices


def compile_path_node(ct_id, object_id):
    return f"{ct_id}:{object_id}"


def decompile_path_node(representation):
    ct_id, object_id = representation.split(":")
    # The value is stored as a string, but the lookup later uses UUID objects as keys so we convert it now.
    # Note that the content type ID is still an integer because we have no control over that model.
    return int(ct_id), uuid.UUID(object_id)


def object_to_path_node(obj):
    """
    Return a representation of an object suitable for inclusion in a CablePath path. Node representation is in the
    form <ContentType ID>:<Object ID>.
    """
    ct = ContentType.objects.get_for_model(obj)
    return compile_path_node(ct.pk, obj.pk)


def path_node_to_object(representation):
    """
    Given the string representation of a path node, return the corresponding instance.
    """
    ct_id, object_id = decompile_path_node(representation)
    ct = ContentType.objects.get_for_id(ct_id)
    return ct.model_class().objects.get(pk=object_id)


def cable_status_color_css(record):
    """
    Given a record such as an Interface, return the CSS needed to apply appropriate coloring to it.
    """
    if not record.cable:
        return ""
    # The status colors are for use with labels and such, and tend to be quite bright.
    # For this function we want a much milder, mellower color suitable as a row background.
    base_color = record.cable.get_status_color().strip("#")
    lighter_color = rgb_to_hex(*lighten_color(*hex_to_rgb(base_color), 0.75))
    return f"background-color: #{lighter_color}"


def validate_interface_tagged_vlans(instance, model, pk_set):
    """
    Validate that the VLANs being added to the 'tagged_vlans' field of an Interface instance are all from the same location
    as the parent device or are global and that the mode of the Interface is set to `InterfaceModeChoices.MODE_TAGGED`.

    Args:
        instance (Interface): The instance of the Interface model that the VLANs are being added to.
        model (Model): The model of the related VLAN objects.
        pk_set (set): The primary keys of the VLAN objects being added to the 'tagged_vlans' field.
    """

    if instance.mode != InterfaceModeChoices.MODE_TAGGED:
        raise ValidationError(
            {"tagged_vlans": f"Mode must be set to {InterfaceModeChoices.MODE_TAGGED} when specifying tagged_vlans"}
        )

    # Filter the model objects based on the primary keys passed in kwargs and exclude the ones that have
    # a location that is not the parent's location or None
    # TODO: after Location model replaced Site, which was not a hierarchical model, should we allow users to add a VLAN
    # belongs to the parent Location or the child location of the parent device to the `tagged_vlan` field of the interface?
    tagged_vlans = (
        model.objects.filter(pk__in=pk_set).exclude(location__isnull=True).exclude(location=instance.parent.location)
    )

    if tagged_vlans.count():
        raise ValidationError(
            {
                "tagged_vlans": (
                    f"Tagged VLAN with names {list(tagged_vlans.values_list('name', flat=True))} must all belong to the "
                    f"same location as the interface's parent device, or it must be global."
                )
            }
        )
