from collections import OrderedDict

from django.db.models import Count, F
from django.shortcuts import render
from django.views.generic import View
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from circuits.filters import CircuitFilter, ProviderFilter
from circuits.models import Circuit, Provider
from circuits.tables import CircuitTable, ProviderTable
from dcim.filters import (
    CableFilter, DeviceFilter, DeviceTypeFilter, PowerFeedFilter, RackFilter, RackGroupFilter, SiteFilter,
    VirtualChassisFilter,
)
from dcim.models import (
    Cable, ConsolePort, Device, DeviceType, Interface, PowerPanel, PowerFeed, PowerPort, Rack, RackGroup, Site, VirtualChassis
)
from dcim.tables import (
    CableTable, DeviceDetailTable, DeviceTypeTable, PowerFeedTable, RackTable, RackGroupTable, SiteTable,
    VirtualChassisTable,
)
from extras.models import ObjectChange, ReportResult, TopologyMap
from ipam.filters import AggregateFilter, IPAddressFilter, PrefixFilter, VLANFilter, VRFFilter
from ipam.models import Aggregate, IPAddress, Prefix, VLAN, VRF
from ipam.tables import AggregateTable, IPAddressTable, PrefixTable, VLANTable, VRFTable
from secrets.filters import SecretFilter
from secrets.models import Secret
from secrets.tables import SecretTable
from tenancy.filters import TenantFilter
from tenancy.models import Tenant
from tenancy.tables import TenantTable
from virtualization.filters import ClusterFilter, VirtualMachineFilter
from virtualization.models import Cluster, VirtualMachine
from virtualization.tables import ClusterTable, VirtualMachineDetailTable
from .forms import SearchForm

SEARCH_MAX_RESULTS = 15
SEARCH_TYPES = OrderedDict((
    # Circuits
    ('provider', {
        'permission': 'circuits.view_provider',
        'queryset': Provider.objects.all(),
        'filter': ProviderFilter,
        'table': ProviderTable,
        'url': 'circuits:provider_list',
    }),
    ('circuit', {
        'permission': 'circuits.view_circuit',
        'queryset': Circuit.objects.prefetch_related(
            'type', 'provider', 'tenant'
        ).prefetch_related(
            'terminations__site'
        ),
        'filter': CircuitFilter,
        'table': CircuitTable,
        'url': 'circuits:circuit_list',
    }),
    # DCIM
    ('site', {
        'permission': 'dcim.view_site',
        'queryset': Site.objects.prefetch_related('region', 'tenant'),
        'filter': SiteFilter,
        'table': SiteTable,
        'url': 'dcim:site_list',
    }),
    ('rack', {
        'permission': 'dcim.view_rack',
        'queryset': Rack.objects.prefetch_related('site', 'group', 'tenant', 'role'),
        'filter': RackFilter,
        'table': RackTable,
        'url': 'dcim:rack_list',
    }),
    ('rackgroup', {
        'permission': 'dcim.view_rackgroup',
        'queryset': RackGroup.objects.prefetch_related('site').annotate(rack_count=Count('racks')),
        'filter': RackGroupFilter,
        'table': RackGroupTable,
        'url': 'dcim:rackgroup_list',
    }),
    ('devicetype', {
        'permission': 'dcim.view_devicetype',
        'queryset': DeviceType.objects.prefetch_related('manufacturer').annotate(instance_count=Count('instances')),
        'filter': DeviceTypeFilter,
        'table': DeviceTypeTable,
        'url': 'dcim:devicetype_list',
    }),
    ('device', {
        'permission': 'dcim.view_device',
        'queryset': Device.objects.prefetch_related(
            'device_type__manufacturer', 'device_role', 'tenant', 'site', 'rack', 'primary_ip4', 'primary_ip6',
        ),
        'filter': DeviceFilter,
        'table': DeviceDetailTable,
        'url': 'dcim:device_list',
    }),
    ('virtualchassis', {
        'permission': 'dcim.view_virtualchassis',
        'queryset': VirtualChassis.objects.prefetch_related('master').annotate(member_count=Count('members')),
        'filter': VirtualChassisFilter,
        'table': VirtualChassisTable,
        'url': 'dcim:virtualchassis_list',
    }),
    ('cable', {
        'permission': 'dcim.view_cable',
        'queryset': Cable.objects.all(),
        'filter': CableFilter,
        'table': CableTable,
        'url': 'dcim:cable_list',
    }),
    ('powerfeed', {
        'permission': 'dcim.view_powerfeed',
        'queryset': PowerFeed.objects.all(),
        'filter': PowerFeedFilter,
        'table': PowerFeedTable,
        'url': 'dcim:powerfeed_list',
    }),
    # Virtualization
    ('cluster', {
        'permission': 'virtualization.view_cluster',
        'queryset': Cluster.objects.prefetch_related('type', 'group'),
        'filter': ClusterFilter,
        'table': ClusterTable,
        'url': 'virtualization:cluster_list',
    }),
    ('virtualmachine', {
        'permission': 'virtualization.view_virtualmachine',
        'queryset': VirtualMachine.objects.prefetch_related(
            'cluster', 'tenant', 'platform', 'primary_ip4', 'primary_ip6',
        ),
        'filter': VirtualMachineFilter,
        'table': VirtualMachineDetailTable,
        'url': 'virtualization:virtualmachine_list',
    }),
    # IPAM
    ('vrf', {
        'permission': 'ipam.view_vrf',
        'queryset': VRF.objects.prefetch_related('tenant'),
        'filter': VRFFilter,
        'table': VRFTable,
        'url': 'ipam:vrf_list',
    }),
    ('aggregate', {
        'permission': 'ipam.view_aggregate',
        'queryset': Aggregate.objects.prefetch_related('rir'),
        'filter': AggregateFilter,
        'table': AggregateTable,
        'url': 'ipam:aggregate_list',
    }),
    ('prefix', {
        'permission': 'ipam.view_prefix',
        'queryset': Prefix.objects.prefetch_related('site', 'vrf__tenant', 'tenant', 'vlan', 'role'),
        'filter': PrefixFilter,
        'table': PrefixTable,
        'url': 'ipam:prefix_list',
    }),
    ('ipaddress', {
        'permission': 'ipam.view_ipaddress',
        'queryset': IPAddress.objects.prefetch_related('vrf__tenant', 'tenant'),
        'filter': IPAddressFilter,
        'table': IPAddressTable,
        'url': 'ipam:ipaddress_list',
    }),
    ('vlan', {
        'permission': 'ipam.view_vlan',
        'queryset': VLAN.objects.prefetch_related('site', 'group', 'tenant', 'role'),
        'filter': VLANFilter,
        'table': VLANTable,
        'url': 'ipam:vlan_list',
    }),
    # Secrets
    ('secret', {
        'permission': 'secrets.view_secret',
        'queryset': Secret.objects.prefetch_related('role', 'device'),
        'filter': SecretFilter,
        'table': SecretTable,
        'url': 'secrets:secret_list',
    }),
    # Tenancy
    ('tenant', {
        'permission': 'tenancy.view_tenant',
        'queryset': Tenant.objects.prefetch_related('group'),
        'filter': TenantFilter,
        'table': TenantTable,
        'url': 'tenancy:tenant_list',
    }),
))


class HomeView(View):
    template_name = 'home.html'

    def get(self, request):

        connected_consoleports = ConsolePort.objects.filter(
            connected_endpoint__isnull=False
        )
        connected_powerports = PowerPort.objects.filter(
            _connected_poweroutlet__isnull=False
        )
        connected_interfaces = Interface.objects.filter(
            _connected_interface__isnull=False,
            pk__lt=F('_connected_interface')
        )
        cables = Cable.objects.all()

        stats = {

            # Organization
            'site_count': Site.objects.count(),
            'tenant_count': Tenant.objects.count(),

            # DCIM
            'rack_count': Rack.objects.count(),
            'devicetype_count': DeviceType.objects.count(),
            'device_count': Device.objects.count(),
            'interface_connections_count': connected_interfaces.count(),
            'cable_count': cables.count(),
            'console_connections_count': connected_consoleports.count(),
            'power_connections_count': connected_powerports.count(),
            'powerpanel_count': PowerPanel.objects.count(),
            'powerfeed_count': PowerFeed.objects.count(),

            # IPAM
            'vrf_count': VRF.objects.count(),
            'aggregate_count': Aggregate.objects.count(),
            'prefix_count': Prefix.objects.count(),
            'ipaddress_count': IPAddress.objects.count(),
            'vlan_count': VLAN.objects.count(),

            # Circuits
            'provider_count': Provider.objects.count(),
            'circuit_count': Circuit.objects.count(),

            # Secrets
            'secret_count': Secret.objects.count(),

            # Virtualization
            'cluster_count': Cluster.objects.count(),
            'virtualmachine_count': VirtualMachine.objects.count(),

        }

        return render(request, self.template_name, {
            'search_form': SearchForm(),
            'stats': stats,
            'topology_maps': TopologyMap.objects.filter(site__isnull=True),
            'report_results': ReportResult.objects.order_by('-created')[:10],
            'changelog': ObjectChange.objects.prefetch_related('user', 'changed_object_type')[:50]
        })


class SearchView(View):

    def get(self, request):

        # No query
        if 'q' not in request.GET:
            return render(request, 'search.html', {
                'form': SearchForm(),
            })

        form = SearchForm(request.GET)
        results = []

        if form.is_valid():

            # Searching for a single type of object
            obj_types = []
            if form.cleaned_data['obj_type']:
                obj_type = form.cleaned_data['obj_type']
                if request.user.has_perm(SEARCH_TYPES[obj_type]['permission']):
                    obj_types.append(form.cleaned_data['obj_type'])
            # Searching all object types
            else:
                for obj_type in SEARCH_TYPES.keys():
                    if request.user.has_perm(SEARCH_TYPES[obj_type]['permission']):
                        obj_types.append(obj_type)

            for obj_type in obj_types:

                queryset = SEARCH_TYPES[obj_type]['queryset']
                filter_cls = SEARCH_TYPES[obj_type]['filter']
                table = SEARCH_TYPES[obj_type]['table']
                url = SEARCH_TYPES[obj_type]['url']

                # Construct the results table for this object type
                filtered_queryset = filter_cls({'q': form.cleaned_data['q']}, queryset=queryset).qs
                table = table(filtered_queryset, orderable=False)
                table.paginate(per_page=SEARCH_MAX_RESULTS)

                if table.page:
                    results.append({
                        'name': queryset.model._meta.verbose_name_plural,
                        'table': table,
                        'url': '{}?q={}'.format(reverse(url), form.cleaned_data['q'])
                    })

        return render(request, 'search.html', {
            'form': form,
            'results': results,
        })


class APIRootView(APIView):
    _ignore_model_permissions = True
    exclude_from_schema = True
    swagger_schema = None

    def get_view_name(self):
        return "API Root"

    def get(self, request, format=None):

        return Response(OrderedDict((
            ('circuits', reverse('circuits-api:api-root', request=request, format=format)),
            ('dcim', reverse('dcim-api:api-root', request=request, format=format)),
            ('extras', reverse('extras-api:api-root', request=request, format=format)),
            ('ipam', reverse('ipam-api:api-root', request=request, format=format)),
            ('secrets', reverse('secrets-api:api-root', request=request, format=format)),
            ('tenancy', reverse('tenancy-api:api-root', request=request, format=format)),
            ('virtualization', reverse('virtualization-api:api-root', request=request, format=format)),
        )))
