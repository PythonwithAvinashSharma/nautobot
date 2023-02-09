import django_tables2 as tables
from django.utils.safestring import mark_safe
from django_tables2.utils import Accessor

from nautobot.core.tables import (
    BaseTable,
    BooleanColumn,
    ButtonsColumn,
    LinkedCountColumn,
    TagColumn,
    ToggleColumn,
)
from nautobot.core.templatetags.helpers import render_boolean
from nautobot.dcim.models import Interface
from nautobot.extras.tables import RoleTableMixin, StatusTableMixin
from nautobot.tenancy.tables import TenantColumn
from nautobot.virtualization.models import VMInterface
from .models import (
    Aggregate,
    IPAddress,
    Prefix,
    RIR,
    RouteTarget,
    Service,
    VLAN,
    VLANGroup,
    VRF,
)

AVAILABLE_LABEL = mark_safe('<span class="label label-success">Available</span>')

UTILIZATION_GRAPH = """
{% load helpers %}
{% if record.present_in_database %}{% utilization_graph record.get_utilization %}{% else %}&mdash;{% endif %}
"""

PREFIX_LINK = """
{% load helpers %}
{% for i in record.parents|as_range %}
    <i class="mdi mdi-circle-small"></i>
{% endfor %}
    <a href="\
{% if record.present_in_database %}\
{% url 'ipam:prefix' pk=record.pk %}\
{% else %}\
{% url 'ipam:prefix_add' %}\
?prefix={{ record }}\
{% if object.vrf %}&vrf={{ object.vrf.pk }}{% endif %}\
{% if object.site %}&site={{ object.site.pk }}{% endif %}\
{% if object.tenant %}&tenant_group={{ object.tenant.tenant_group.pk }}&tenant={{ object.tenant.pk }}{% endif %}\
{% endif %}\
">{{ record.prefix }}</a>
"""

PREFIX_COPY_LINK = """
{% load helpers %}
{% for i in record.parents|as_range %}
    <i class="mdi mdi-circle-small"></i>
{% endfor %}
<span class="hover_copy">
  <a href="\
{% if record.present_in_database %}\
{% url 'ipam:prefix' pk=record.pk %}\
{% else %}\
{% url 'ipam:prefix_add' %}\
?prefix={{ record }}\
{% if object.vrf %}&vrf={{ object.vrf.pk }}{% endif %}\
{% if object.site %}&site={{ object.site.pk }}{% endif %}\
{% if object.tenant %}&tenant_group={{ object.tenant.tenant_group.pk }}&tenant={{ object.tenant.pk }}{% endif %}\
{% endif %}\
" id="copy_{{record.id}}">{{ record.prefix }}</a>
  <button type="button" class="btn btn-inline btn-default hover_copy_button" data-clipboard-target="#copy_{{record.id}}">
    <span class="mdi mdi-content-copy"></span>
  </button>
</span>
"""

PREFIX_ROLE_LINK = """
{% if record.role %}
    <a href="{% url 'ipam:prefix_list' %}?role={{ record.role.slug }}">{{ record.role }}</a>
{% else %}
    &mdash;
{% endif %}
"""

IPADDRESS_LINK = """
{% if record.present_in_database %}
    <a href="{{ record.get_absolute_url }}">{{ record.address }}</a>
{% elif perms.ipam.add_ipaddress %}
    <a href="\
{% url 'ipam:ipaddress_add' %}\
?address={{ record.1 }}\
{% if object.vrf %}&vrf={{ object.vrf.pk }}{% endif %}\
{% if object.tenant %}&tenant={{ object.tenant.pk }}{% endif %}\
" class="btn btn-xs btn-success">\
{% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} IP{{ record.0|pluralize }} available</a>
{% else %}
    {% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} IP{{ record.0|pluralize }} available
{% endif %}
"""

IPADDRESS_COPY_LINK = """
{% if record.present_in_database %}
    <span class="hover_copy">
        <a href="{{ record.get_absolute_url }}" id="copy_{{record.id}}">
            {{ record.address }}</a>
        <button type="button" class="btn btn-inline btn-default hover_copy_button" data-clipboard-target="#copy_{{record.id}}">
            <span class="mdi mdi-content-copy"></span>
        </button>
    </span>
{% elif perms.ipam.add_ipaddress %}
    <a href="\
{% url 'ipam:ipaddress_add' %}\
?address={{ record.1 }}\
{% if object.vrf %}&vrf={{ object.vrf.pk }}{% endif %}\
{% if object.tenant %}&tenant={{ object.tenant.pk }}{% endif %}\
" class="btn btn-xs btn-success">\
{% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} IP{{ record.0|pluralize }} available</a>
{% else %}
    {% if record.0 <= 65536 %}{{ record.0 }}{% else %}Many{% endif %} IP{{ record.0|pluralize }} available
{% endif %}
"""

IPADDRESS_ASSIGN_LINK = """
<a href="\
{% url 'ipam:ipaddress_edit' pk=record.pk %}\
?{% if request.GET.interface %}interface={{ request.GET.interface }}\
{% elif request.GET.vminterface %}\
vminterface={{ request.GET.vminterface }}{% endif %}\
&return_url={{ request.GET.return_url }}">{{ record }}</a>
"""

IPADDRESS_ASSIGN_COPY_LINK = """
<span class="hover_copy">
<a href="\
{% url 'ipam:ipaddress_edit' pk=record.pk %}\
?{% if request.GET.interface %}\
interface={{ request.GET.interface }}\
{% elif request.GET.vminterface %}\
vminterface={{ request.GET.vminterface }}\
{% endif %}\
&return_url={{ request.GET.return_url }}" id="copy_{{record.pk}}">\
{{ record }}\
</a><button type="button" class="btn btn-inline btn-default hover_copy_button" data-clipboard-target="#copy_{{record.pk}}">
    <span class="mdi mdi-content-copy"></span>
</button>
</span>
"""

VRF_LINK = """
{% if record.vrf %}
    <a href="{{ record.vrf.get_absolute_url }}">{{ record.vrf }}</a>
{% elif object.vrf %}
    <a href="{{ object.vrf.get_absolute_url }}">{{ object.vrf }}</a>
{% else %}
    Global
{% endif %}
"""

VRF_TARGETS = """
{% for rt in value.all %}
    <a href="{{ rt.get_absolute_url }}">{{ rt }}</a>{% if not forloop.last %}<br />{% endif %}
{% empty %}
    &mdash;
{% endfor %}
"""

VLAN_LINK = """
{% if record.present_in_database %}
    <a href="{{ record.get_absolute_url }}">{{ record.vid }}</a>
{% elif perms.ipam.add_vlan %}
    <a href="\
{% url 'ipam:vlan_add' %}\
?vid={{ record.vid }}&vlan_group={{ vlan_group.pk }}\
{% if vlan_group.site %}&site={{ vlan_group.site.pk }}{% endif %}\
{% if vlan_group.location %}&location={{ vlan_group.location.pk }}{% endif %}\
" class="btn btn-xs btn-success">{{ record.available }} VLAN{{ record.available|pluralize }} available</a>\
{% else %}
    {{ record.available }} VLAN{{ record.available|pluralize }} available
{% endif %}
"""

VLAN_PREFIXES = """
{% for prefix in record.prefixes.all %}
    <a href="{% url 'ipam:prefix' pk=prefix.pk %}">{{ prefix }}</a>{% if not forloop.last %}<br />{% endif %}
{% empty %}
    &mdash;
{% endfor %}
"""

VLAN_ROLE_LINK = """
{% if record.role %}
    <a href="{% url 'ipam:vlan_list' %}?role={{ record.role.slug }}">{{ record.role }}</a>
{% else %}
    &mdash;
{% endif %}
"""

VLANGROUP_ADD_VLAN = """
{% with next_vid=record.get_next_available_vid %}
    {% if next_vid and perms.ipam.add_vlan %}
        <a href="\
{% url 'ipam:vlan_add' %}\
?site={{ record.site_id }}\
{% if record.location %}&location={{ record.location_id }}{% endif %}\
&vlan_group={{ record.pk }}&vid={{ next_vid }}\
" title="Add VLAN" class="btn btn-xs btn-success"><i class="mdi mdi-plus-thick" aria-hidden="true"></i></a>
    {% endif %}
{% endwith %}
"""

#
# VRFs
#


class VRFTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    rd = tables.Column(verbose_name="RD")
    tenant = TenantColumn()
    enforce_unique = BooleanColumn(verbose_name="Unique")
    import_targets = tables.TemplateColumn(template_code=VRF_TARGETS, orderable=False)
    export_targets = tables.TemplateColumn(template_code=VRF_TARGETS, orderable=False)
    tags = TagColumn(url_name="ipam:vrf_list")

    class Meta(BaseTable.Meta):
        model = VRF
        fields = (
            "pk",
            "name",
            "rd",
            "tenant",
            "enforce_unique",
            "description",
            "import_targets",
            "export_targets",
            "tags",
        )
        default_columns = ("pk", "name", "rd", "tenant", "description")


#
# Route targets
#


class RouteTargetTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    tenant = TenantColumn()
    tags = TagColumn(url_name="ipam:vrf_list")

    class Meta(BaseTable.Meta):
        model = RouteTarget
        fields = ("pk", "name", "tenant", "description", "tags")
        default_columns = ("pk", "name", "tenant", "description")


#
# RIRs
#


class RIRTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    is_private = BooleanColumn(verbose_name="Private")
    aggregate_count = LinkedCountColumn(
        viewname="ipam:aggregate_list",
        url_params={"rir": "slug"},
        verbose_name="Aggregates",
    )
    actions = ButtonsColumn(RIR, pk_field="slug")

    class Meta(BaseTable.Meta):
        model = RIR
        fields = (
            "pk",
            "name",
            "slug",
            "is_private",
            "aggregate_count",
            "description",
            "actions",
        )
        default_columns = (
            "pk",
            "name",
            "is_private",
            "aggregate_count",
            "description",
            "actions",
        )


#
# Aggregates
#


class AggregateTable(BaseTable):
    pk = ToggleColumn()
    prefix = tables.LinkColumn(verbose_name="Aggregate", order_by=("network", "prefix_length"))
    rir = tables.Column(linkify=True)
    tenant = TenantColumn()
    date_added = tables.DateColumn(format="Y-m-d", verbose_name="Added")

    class Meta(BaseTable.Meta):
        model = Aggregate
        fields = ("pk", "prefix", "rir", "tenant", "date_added", "description")


class AggregateDetailTable(AggregateTable):
    child_count = tables.Column(verbose_name="Prefixes")
    utilization = tables.TemplateColumn(template_code=UTILIZATION_GRAPH, orderable=False)
    tags = TagColumn(url_name="ipam:aggregate_list")

    class Meta(AggregateTable.Meta):
        fields = (
            "pk",
            "prefix",
            "rir",
            "tenant",
            "child_count",
            "utilization",
            "date_added",
            "description",
            "tags",
        )
        default_columns = (
            "pk",
            "prefix",
            "rir",
            "tenant",
            "child_count",
            "utilization",
            "date_added",
            "description",
        )


#
# Prefixes
#


class PrefixTable(StatusTableMixin, RoleTableMixin, BaseTable):
    pk = ToggleColumn()
    prefix = tables.TemplateColumn(
        template_code=PREFIX_COPY_LINK, attrs={"td": {"class": "text-nowrap"}}, order_by=("network", "prefix_length")
    )
    vrf = tables.TemplateColumn(template_code=VRF_LINK, verbose_name="VRF")
    tenant = TenantColumn()
    site = tables.Column(linkify=True)
    location = tables.Column(linkify=True)
    vlan = tables.Column(linkify=True, verbose_name="VLAN")

    class Meta(BaseTable.Meta):
        model = Prefix
        fields = (
            "pk",
            "prefix",
            "type",
            "status",
            "children",
            "vrf",
            "tenant",
            "site",
            "location",
            "vlan",
            "role",
            "description",
        )
        default_columns = (
            "pk",
            "prefix",
            "type",
            "status",
            "vrf",
            "tenant",
            "site",
            "location",
            "vlan",
            "role",
            "description",
        )
        row_attrs = {
            "class": lambda record: "success" if not record.present_in_database else "",
        }


class PrefixDetailTable(PrefixTable):
    utilization = tables.TemplateColumn(template_code=UTILIZATION_GRAPH, orderable=False)
    tenant = TenantColumn()
    tags = TagColumn(url_name="ipam:prefix_list")

    class Meta(PrefixTable.Meta):
        fields = (
            "pk",
            "prefix",
            "type",
            "status",
            "children",
            "vrf",
            "utilization",
            "tenant",
            "site",
            "location",
            "vlan",
            "role",
            "description",
            "tags",
        )
        default_columns = (
            "pk",
            "prefix",
            "type",
            "status",
            "children",
            "vrf",
            "utilization",
            "tenant",
            "site",
            "location",
            "vlan",
            "role",
            "description",
        )


#
# IPAddresses
#


class IPAddressTable(StatusTableMixin, RoleTableMixin, BaseTable):
    pk = ToggleColumn()
    address = tables.TemplateColumn(
        template_code=IPADDRESS_COPY_LINK, verbose_name="IP Address", order_by=("host", "prefix_length")
    )
    vrf = tables.TemplateColumn(template_code=VRF_LINK, verbose_name="VRF")
    tenant = TenantColumn()
    assigned_object = tables.Column(linkify=True, orderable=False, verbose_name="Interface")
    assigned_object_parent = tables.Column(
        accessor="assigned_object__parent",
        linkify=True,
        orderable=False,
        verbose_name="Interface Parent",
    )

    class Meta(BaseTable.Meta):
        model = IPAddress
        fields = (
            "pk",
            "address",
            "vrf",
            "status",
            "role",
            "tenant",
            "assigned_object",
            "assigned_object_parent",
            "dns_name",
            "description",
        )
        row_attrs = {
            "class": lambda record: "success" if not isinstance(record, IPAddress) else "",
        }


class IPAddressDetailTable(IPAddressTable):
    nat_inside = tables.Column(linkify=True, orderable=False, verbose_name="NAT (Inside)")
    tenant = TenantColumn()
    assigned = BooleanColumn(accessor="assigned_object_id", verbose_name="Assigned")
    tags = TagColumn(url_name="ipam:ipaddress_list")

    class Meta(IPAddressTable.Meta):
        fields = (
            "pk",
            "address",
            "vrf",
            "status",
            "role",
            "tenant",
            "nat_inside",
            "assigned",
            "dns_name",
            "description",
            "tags",
        )
        default_columns = (
            "pk",
            "address",
            "vrf",
            "status",
            "role",
            "tenant",
            "assigned",
            "dns_name",
            "description",
        )


class IPAddressAssignTable(StatusTableMixin, BaseTable):
    address = tables.TemplateColumn(template_code=IPADDRESS_ASSIGN_COPY_LINK, verbose_name="IP Address")
    assigned_object = tables.Column(orderable=False)

    class Meta(BaseTable.Meta):
        model = IPAddress
        fields = (
            "address",
            "dns_name",
            "vrf",
            "status",
            "role",
            "tenant",
            "assigned_object",
            "description",
        )
        orderable = False


class InterfaceIPAddressTable(StatusTableMixin, BaseTable):
    """
    List IP addresses assigned to a specific Interface.
    """

    address = tables.TemplateColumn(template_code=IPADDRESS_ASSIGN_COPY_LINK, verbose_name="IP Address")
    vrf = tables.TemplateColumn(template_code=VRF_LINK, verbose_name="VRF")
    tenant = TenantColumn()

    class Meta(BaseTable.Meta):
        model = IPAddress
        fields = ("address", "vrf", "status", "role", "tenant", "description")


#
# VLAN groups
#


class VLANGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    site = tables.Column(linkify=True)
    location = tables.Column(linkify=True)
    vlan_count = LinkedCountColumn(viewname="ipam:vlan_list", url_params={"vlan_group": "slug"}, verbose_name="VLANs")
    actions = ButtonsColumn(model=VLANGroup, prepend_template=VLANGROUP_ADD_VLAN)

    class Meta(BaseTable.Meta):
        model = VLANGroup
        fields = ("pk", "name", "site", "location", "vlan_count", "slug", "description", "actions")
        default_columns = ("pk", "name", "site", "location", "vlan_count", "description", "actions")


#
# VLANs
#


class VLANTable(StatusTableMixin, RoleTableMixin, BaseTable):
    pk = ToggleColumn()
    vid = tables.TemplateColumn(template_code=VLAN_LINK, verbose_name="ID")
    site = tables.Column(linkify=True)
    location = tables.Column(linkify=True)
    vlan_group = tables.Column(linkify=True)
    tenant = TenantColumn()

    class Meta(BaseTable.Meta):
        model = VLAN
        fields = (
            "pk",
            "vid",
            "site",
            "location",
            "vlan_group",
            "name",
            "tenant",
            "status",
            "role",
            "description",
        )
        row_attrs = {
            "class": lambda record: "success" if not isinstance(record, VLAN) else "",
        }


class VLANDetailTable(VLANTable):
    prefixes = tables.TemplateColumn(template_code=VLAN_PREFIXES, orderable=False, verbose_name="Prefixes")
    tenant = TenantColumn()
    tags = TagColumn(url_name="ipam:vlan_list")

    class Meta(VLANTable.Meta):
        fields = (
            "pk",
            "vid",
            "site",
            "location",
            "vlan_group",
            "name",
            "prefixes",
            "tenant",
            "status",
            "role",
            "description",
            "tags",
        )
        default_columns = (
            "pk",
            "vid",
            "site",
            "location",
            "vlan_group",
            "name",
            "prefixes",
            "tenant",
            "status",
            "role",
            "description",
        )


class VLANMembersTable(BaseTable):
    """
    Base table for Interface and VMInterface assignments
    """

    name = tables.LinkColumn(verbose_name="Interface")
    tagged = tables.Column(empty_values=(), orderable=False)

    def render_tagged(self, value, record):
        return render_boolean(record.untagged_vlan_id != self.context["object"].pk)


class VLANDevicesTable(VLANMembersTable):
    device = tables.LinkColumn()
    actions = ButtonsColumn(Interface, buttons=["edit"])

    class Meta(BaseTable.Meta):
        model = Interface
        fields = ("device", "name", "tagged", "actions")


class VLANVirtualMachinesTable(VLANMembersTable):
    virtual_machine = tables.LinkColumn()
    actions = ButtonsColumn(VMInterface, buttons=["edit"])

    class Meta(BaseTable.Meta):
        model = VMInterface
        fields = ("virtual_machine", "name", "tagged", "actions")


class InterfaceVLANTable(StatusTableMixin, BaseTable):
    """
    List VLANs assigned to a specific Interface.
    """

    vid = tables.LinkColumn(viewname="ipam:vlan", args=[Accessor("pk")], verbose_name="ID")
    tagged = BooleanColumn()
    site = tables.Column(linkify=True)
    location = tables.Column(linkify=True)
    vlan_group = tables.Column(accessor=Accessor("vlan_group__name"), verbose_name="Group")
    tenant = TenantColumn()
    role = tables.TemplateColumn(template_code=VLAN_ROLE_LINK)

    class Meta(BaseTable.Meta):
        model = VLAN
        fields = (
            "vid",
            "tagged",
            "site",
            "location",
            "vlan_group",
            "name",
            "tenant",
            "status",
            "role",
            "description",
        )

    def __init__(self, interface, *args, **kwargs):
        self.interface = interface
        super().__init__(*args, **kwargs)


#
# Services
#


class ServiceTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    parent = tables.LinkColumn(order_by=("device", "virtual_machine"))
    ports = tables.TemplateColumn(template_code="{{ record.port_list }}", verbose_name="Ports")
    tags = TagColumn(url_name="ipam:service_list")

    class Meta(BaseTable.Meta):
        model = Service
        fields = (
            "pk",
            "name",
            "parent",
            "protocol",
            "ports",
            "ip_addresses",
            "description",
            "tags",
        )
        default_columns = ("pk", "name", "parent", "protocol", "ports", "description")
