from django import forms

from nautobot.core.forms import (
    add_blank_choice,
    AddressFieldMixin,
    BootstrapMixin,
    DateTimePicker,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
    ExpandableIPAddressField,
    NumericArrayField,
    PrefixFieldMixin,
    ReturnURLForm,
    SlugField,
    StaticSelect2,
    StaticSelect2Multiple,
    TagFilterField,
)
from nautobot.core.forms.constants import BOOLEAN_WITH_BLANK_CHOICES
from nautobot.dcim.form_mixins import (
    LocatableModelBulkEditFormMixin,
    LocatableModelFilterFormMixin,
    LocatableModelFormMixin,
)
from nautobot.dcim.models import Device, Location, Rack
from nautobot.extras.forms import (
    NautobotBulkEditForm,
    NautobotModelForm,
    NautobotFilterForm,
    RoleModelBulkEditFormMixin,
    RoleModelFilterFormMixin,
    StatusModelBulkEditFormMixin,
    StatusModelFilterFormMixin,
    TagsBulkEditFormMixin,
)
from nautobot.tenancy.forms import TenancyFilterForm, TenancyForm
from nautobot.tenancy.models import Tenant
from nautobot.virtualization.models import Cluster, VirtualMachine
from .choices import IPAddressVersionChoices, ServiceProtocolChoices, PrefixTypeChoices
from .constants import (
    IPADDRESS_MASK_LENGTH_MIN,
    IPADDRESS_MASK_LENGTH_MAX,
    PREFIX_LENGTH_MAX,
    PREFIX_LENGTH_MIN,
    SERVICE_PORT_MAX,
    SERVICE_PORT_MIN,
)
from .models import (
    IPAddress,
    IPAddressToInterface,
    Namespace,
    Prefix,
    RIR,
    RouteTarget,
    Service,
    VLAN,
    VLANGroup,
    VRF,
)

PREFIX_MASK_LENGTH_CHOICES = add_blank_choice([(i, i) for i in range(PREFIX_LENGTH_MIN, PREFIX_LENGTH_MAX + 1)])

IPADDRESS_MASK_LENGTH_CHOICES = add_blank_choice(
    [(i, i) for i in range(IPADDRESS_MASK_LENGTH_MIN, IPADDRESS_MASK_LENGTH_MAX + 1)]
)


#
# Namespaces
#


class NamespaceForm(LocatableModelFormMixin, NautobotModelForm):
    class Meta:
        model = Namespace
        fields = ["name", "description", "location"]


#
# VRFs
#


class VRFForm(NautobotModelForm, TenancyForm):
    import_targets = DynamicModelMultipleChoiceField(queryset=RouteTarget.objects.all(), required=False)
    export_targets = DynamicModelMultipleChoiceField(queryset=RouteTarget.objects.all(), required=False)
    namespace = DynamicModelChoiceField(queryset=Namespace.objects.all())
    devices = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False)
    virtual_machines = DynamicModelMultipleChoiceField(queryset=VirtualMachine.objects.all(), required=False)
    prefixes = DynamicModelMultipleChoiceField(
        queryset=Prefix.objects.all(),
        required=False,
        query_params={
            "namespace": "$namespace",
        },
    )

    class Meta:
        model = VRF
        fields = [
            "name",
            "rd",
            "namespace",
            "description",
            "import_targets",
            "export_targets",
            "tenant_group",
            "tenant",
            "tags",
            "devices",
            "virtual_machines",
            "prefixes",
        ]
        labels = {
            "rd": "RD",
        }
        help_texts = {
            "rd": "Route distinguisher unique to this Namespace (as defined in RFC 4364)",
        }


class VRFBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=VRF.objects.all(), widget=forms.MultipleHiddenInput())
    namespace = DynamicModelChoiceField(queryset=Namespace.objects.all(), required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = [
            "tenant",
            "description",
        ]


class VRFFilterForm(NautobotFilterForm, TenancyFilterForm):
    model = VRF
    field_order = ["q", "import_target", "export_target", "tenant_group", "tenant"]
    q = forms.CharField(required=False, label="Search")
    import_target = DynamicModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(), to_field_name="name", required=False
    )
    export_target = DynamicModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(), to_field_name="name", required=False
    )
    tag = TagFilterField(model)


#
# Route targets
#


class RouteTargetForm(NautobotModelForm, TenancyForm):
    class Meta:
        model = RouteTarget
        fields = [
            "name",
            "description",
            "tenant_group",
            "tenant",
            "tags",
        ]


class RouteTargetBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=RouteTarget.objects.all(), widget=forms.MultipleHiddenInput())
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    description = forms.CharField(max_length=200, required=False)

    class Meta:
        nullable_fields = [
            "tenant",
            "description",
        ]


class RouteTargetFilterForm(NautobotFilterForm, TenancyFilterForm):
    model = RouteTarget
    field_order = [
        "q",
        "name",
        "tenant_group",
        "tenant",
        "importing_vrfs",
        "exporting_vrfs",
    ]
    q = forms.CharField(required=False, label="Search")
    importing_vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(), required=False, label="Imported by VRF"
    )
    exporting_vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(), required=False, label="Exported by VRF"
    )
    tag = TagFilterField(model)


#
# RIRs
#


class RIRForm(NautobotModelForm):
    class Meta:
        model = RIR
        fields = [
            "name",
            "is_private",
            "description",
        ]


class RIRFilterForm(NautobotFilterForm):
    model = RIR
    is_private = forms.NullBooleanField(
        required=False,
        label="Private",
        widget=StaticSelect2(choices=BOOLEAN_WITH_BLANK_CHOICES),
    )


#
# Prefixes
#


class PrefixForm(LocatableModelFormMixin, NautobotModelForm, TenancyForm, PrefixFieldMixin):
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label="VLAN group",
        null_option="None",
        query_params={"location_id": "$location"},
        initial_params={"vlans": "$vlan"},
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label="VLAN",
        query_params={
            "location": "$location",
            "group_id": "$vlan_group",
        },
    )
    rir = DynamicModelChoiceField(queryset=RIR.objects.all(), required=False, label="RIR")
    namespace = DynamicModelChoiceField(queryset=Namespace.objects.all())
    vrfs = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label="VRFs",
        query_params={
            "namespace": "$namespace",
        },
    )

    class Meta:
        model = Prefix
        fields = [
            "prefix",
            "namespace",
            "vrfs",
            "location",
            "vlan",
            "status",
            "role",
            "type",
            "description",
            "tenant_group",
            "tenant",
            "rir",
            "date_allocated",
            "tags",
        ]
        widgets = {
            "date_allocated": DateTimePicker(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance is not None:
            self.initial["vrfs"] = self.instance.vrfs.values_list("id", flat=True)

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        instance.vrfs.set(self.cleaned_data["vrfs"])
        return instance


class PrefixBulkEditForm(
    TagsBulkEditFormMixin,
    LocatableModelBulkEditFormMixin,
    StatusModelBulkEditFormMixin,
    RoleModelBulkEditFormMixin,
    NautobotBulkEditForm,
):
    pk = forms.ModelMultipleChoiceField(queryset=Prefix.objects.all(), widget=forms.MultipleHiddenInput())
    type = forms.ChoiceField(
        choices=add_blank_choice(PrefixTypeChoices),
        required=False,
    )
    """
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label="VRF",
    )
    """
    prefix_length = forms.IntegerField(min_value=PREFIX_LENGTH_MIN, max_value=PREFIX_LENGTH_MAX, required=False)
    namespace = DynamicModelChoiceField(queryset=Namespace.objects.all(), required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    rir = DynamicModelChoiceField(queryset=RIR.objects.all(), required=False, label="RIR")
    date_allocated = forms.DateTimeField(required=False, widget=DateTimePicker)
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Prefix
        nullable_fields = [
            "location",
            # "vrf",
            "tenant",
            "rir",
            "date_allocated",
            "description",
        ]


class PrefixFilterForm(
    NautobotFilterForm,
    LocatableModelFilterFormMixin,
    TenancyFilterForm,
    StatusModelFilterFormMixin,
    RoleModelFilterFormMixin,
):
    model = Prefix
    field_order = [
        "q",
        "within_include",
        "type",
        "ip_version",
        "mask_length",
        # "vrf_id",
        # "present_in_vrf_id",
        "status",
        "location",
        "role",
        "tenant_group",
        "tenant",
        "rir",
    ]
    mask_length__lte = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    q = forms.CharField(required=False, label="Search")
    within_include = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Prefix",
            }
        ),
        label="Search within",
    )
    ip_version = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressVersionChoices),
        label="IP version",
        widget=StaticSelect2(),
    )
    mask_length = forms.ChoiceField(
        required=False,
        choices=PREFIX_MASK_LENGTH_CHOICES,
        label="Mask length",
        widget=StaticSelect2(),
    )
    """
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label="Assigned VRF",
        null_option="Global",
    )
    present_in_vrf_id = DynamicModelChoiceField(queryset=VRF.objects.all(), required=False, label="Present in VRF")
    """
    type = forms.MultipleChoiceField(
        required=False,
        choices=PrefixTypeChoices,
        widget=StaticSelect2Multiple(),
    )
    rir = DynamicModelChoiceField(queryset=RIR.objects.all(), required=False, label="RIR")
    tag = TagFilterField(model)


#
# IP addresses
#


class IPAddressForm(NautobotModelForm, TenancyForm, ReturnURLForm, AddressFieldMixin):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label="VRF",
    )
    nat_location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label="Location",
    )
    nat_rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label="Rack",
        null_option="None",
        query_params={"location": "$nat_location"},
    )
    nat_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label="Device",
        query_params={
            "location": "$nat_location",
            "rack": "$nat_rack",
        },
    )
    nat_cluster = DynamicModelChoiceField(queryset=Cluster.objects.all(), required=False, label="Cluster")
    nat_virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label="Virtual Machine",
        query_params={
            "cluster_id": "$nat_cluster",
        },
    )
    nat_vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label="VRF",
    )
    nat_inside = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label="IP Address",
        query_params={
            "device_id": "$nat_device",
            "virtual_machine_id": "$nat_virtual_machine",
            "vrf_id": "$nat_vrf",
        },
    )
    namespace = DynamicModelChoiceField(queryset=Namespace.objects.all())

    class Meta:
        model = IPAddress
        fields = [
            "address",
            "namespace",
            "vrf",
            "status",
            "role",
            "dns_name",
            "description",
            "nat_rack",
            "nat_device",
            "nat_cluster",
            "nat_virtual_machine",
            "nat_vrf",
            "nat_inside",
            "tenant_group",
            "tenant",
            "tags",
        ]

    def clean_namespace(self):
        """
        Explicitly set the Namespace on the instance so it will be used on save.

        While the model does this itself on create, the model form is creating a bare instance first
        and setting attributes individually based on the form field values. Since namespace isn't an
        actual model field, it gets ignored by default.
        """
        namespace = self.cleaned_data.pop("namespace")
        setattr(self.instance, "_namespace", namespace)

    def __init__(self, *args, **kwargs):
        # Initialize helper selectors
        instance = kwargs.get("instance")
        initial = kwargs.get("initial", {}).copy()

        if instance:
            if instance.nat_inside:
                # TODO: Does this make sense with ip address to interface relationship changing to m2m?
                nat_inside_parent = IPAddressToInterface.objects.filter(ip_address=instance.nat_inside)
                if nat_inside_parent.count() == 1:
                    nat_inside_parent = nat_inside_parent.first()
                    if nat_inside_parent.interface is not None:
                        initial["nat_location"] = nat_inside_parent.interface.device.location.pk
                        if nat_inside_parent.interface.device.rack:
                            initial["nat_rack"] = nat_inside_parent.interface.device.rack.pk
                        initial["nat_device"] = nat_inside_parent.interface.device.pk
                    elif nat_inside_parent.vm_interface is not None:
                        initial["nat_cluster"] = nat_inside_parent.vm_interface.virtual_machine.cluster.pk
                        initial["nat_virtual_machine"] = nat_inside_parent.vm_interface.virtual_machine.pk

            # Always populate the namespace from the parent.
            if instance.present_in_database:
                initial["namespace"] = instance.parent.namespace

        kwargs["initial"] = initial

        super().__init__(*args, **kwargs)

        self.fields["vrf"].empty_label = "Global"


class IPAddressBulkCreateForm(BootstrapMixin, forms.Form):
    pattern = ExpandableIPAddressField(label="Address pattern")


class IPAddressBulkAddForm(NautobotModelForm, TenancyForm, AddressFieldMixin):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label="VRF",
    )

    class Meta:
        model = IPAddress
        fields = [
            "address",
            "vrf",
            "status",
            "role",
            "dns_name",
            "description",
            "tenant_group",
            "tenant",
            "tags",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["vrf"].empty_label = "Global"


class IPAddressBulkEditForm(
    TagsBulkEditFormMixin, StatusModelBulkEditFormMixin, RoleModelBulkEditFormMixin, NautobotBulkEditForm
):
    pk = forms.ModelMultipleChoiceField(queryset=IPAddress.objects.all(), widget=forms.MultipleHiddenInput())
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label="VRF",
    )
    mask_length = forms.IntegerField(
        min_value=IPADDRESS_MASK_LENGTH_MIN,
        max_value=IPADDRESS_MASK_LENGTH_MAX,
        required=False,
    )
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    dns_name = forms.CharField(max_length=255, required=False)
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = [
            "vrf",
            "tenant",
            "dns_name",
            "description",
        ]


class IPAddressAssignForm(BootstrapMixin, forms.Form):
    vrf_id = DynamicModelChoiceField(queryset=VRF.objects.all(), required=False, label="VRF", empty_label="Global")
    q = forms.CharField(
        required=False,
        label="Search",
    )


class IPAddressFilterForm(NautobotFilterForm, TenancyFilterForm, StatusModelFilterFormMixin, RoleModelFilterFormMixin):
    model = IPAddress
    field_order = [
        "q",
        "parent",
        "ip_version",
        "mask_length",
        "vrf_id",
        "present_in_vrf_id",
        "status",
        "role",
        "tenant_group",
        "tenant",
    ]
    q = forms.CharField(required=False, label="Search")
    parent = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Prefix",
            }
        ),
        label="Parent Prefix",
    )
    ip_version = forms.ChoiceField(
        required=False,
        choices=add_blank_choice(IPAddressVersionChoices),
        label="IP version",
        widget=StaticSelect2(),
    )
    mask_length = forms.ChoiceField(
        required=False,
        choices=IPADDRESS_MASK_LENGTH_CHOICES,
        label="Mask length",
        widget=StaticSelect2(),
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label="Assigned VRF",
        null_option="Global",
    )
    present_in_vrf_id = DynamicModelChoiceField(queryset=VRF.objects.all(), required=False, label="Present in VRF")
    tag = TagFilterField(model)


#
# VLAN groups
#


class VLANGroupForm(LocatableModelFormMixin, NautobotModelForm):
    slug = SlugField()

    class Meta:
        model = VLANGroup
        fields = [
            "location",
            "name",
            "slug",
            "description",
        ]


class VLANGroupFilterForm(NautobotFilterForm, LocatableModelFilterFormMixin):
    model = VLANGroup


#
# VLANs
#


class VLANForm(LocatableModelFormMixin, NautobotModelForm, TenancyForm):
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        query_params={"location": "$location"},
    )

    class Meta:
        model = VLAN
        fields = [
            "location",
            "vlan_group",
            "vid",
            "name",
            "status",
            "role",
            "description",
            "tenant_group",
            "tenant",
            "tags",
        ]
        help_texts = {
            "location": "Leave blank if this VLAN spans multiple locations",
            "vlan_group": "VLAN group (optional)",
            "vid": "Configured VLAN ID",
            "name": "Configured VLAN name",
            "status": "Operational status of this VLAN",
            "role": "The primary function of this VLAN",
        }


class VLANBulkEditForm(
    TagsBulkEditFormMixin,
    LocatableModelBulkEditFormMixin,
    StatusModelBulkEditFormMixin,
    RoleModelBulkEditFormMixin,
    NautobotBulkEditForm,
):
    pk = forms.ModelMultipleChoiceField(queryset=VLAN.objects.all(), widget=forms.MultipleHiddenInput())
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        query_params={"location_id": "$location"},
    )
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        model = VLAN
        nullable_fields = [
            "location",
            "vlan_group",
            "tenant",
            "description",
        ]


class VLANFilterForm(
    NautobotFilterForm,
    LocatableModelFilterFormMixin,
    TenancyFilterForm,
    StatusModelFilterFormMixin,
    RoleModelFilterFormMixin,
):
    model = VLAN
    field_order = [
        "q",
        "location",
        "group_id",
        "status",
        "role",
        "tenant_group",
        "tenant",
    ]
    q = forms.CharField(required=False, label="Search")
    group_id = DynamicModelMultipleChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label="VLAN group",
        null_option="None",
        query_params={"location": "$location"},
    )
    tag = TagFilterField(model)


#
# Services
#


class ServiceForm(NautobotModelForm):
    ports = NumericArrayField(
        base_field=forms.IntegerField(min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX),
        help_text="Comma-separated list of one or more port numbers. A range may be specified using a hyphen.",
    )

    class Meta:
        model = Service
        fields = [
            "name",
            "protocol",
            "ports",
            "ip_addresses",
            "description",
            "tags",
        ]
        help_texts = {
            "ip_addresses": "IP address assignment is optional. If no IPs are selected, the service is assumed to be "
            "reachable via all IPs assigned to the device.",
        }
        widgets = {
            "protocol": StaticSelect2(),
            "ip_addresses": StaticSelect2Multiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit IP address choices to those assigned to interfaces of the parent device/VM
        if self.instance.device:
            self.fields["ip_addresses"].queryset = IPAddress.objects.filter(
                interfaces__in=self.instance.device.vc_interfaces.values_list("id", flat=True)
            )
        elif self.instance.virtual_machine:
            self.fields["ip_addresses"].queryset = IPAddress.objects.filter(
                vm_interfaces__in=self.instance.virtual_machine.interfaces.values_list("id", flat=True)
            )
        else:
            self.fields["ip_addresses"].choices = []


class ServiceFilterForm(NautobotFilterForm):
    model = Service
    q = forms.CharField(required=False, label="Search")
    protocol = forms.ChoiceField(
        choices=add_blank_choice(ServiceProtocolChoices),
        required=False,
        widget=StaticSelect2Multiple(),
    )
    port = forms.IntegerField(
        required=False,
    )
    tag = TagFilterField(model)


class ServiceBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Service.objects.all(), widget=forms.MultipleHiddenInput())
    protocol = forms.ChoiceField(
        choices=add_blank_choice(ServiceProtocolChoices),
        required=False,
        widget=StaticSelect2(),
    )
    ports = NumericArrayField(
        base_field=forms.IntegerField(min_value=SERVICE_PORT_MIN, max_value=SERVICE_PORT_MAX),
        required=False,
    )
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = [
            "description",
        ]
