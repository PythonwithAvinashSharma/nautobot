from django.contrib import messages
from django.db import transaction
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from dcim.models import Device
from dcim.tables import DeviceTable
from extras.views import ObjectConfigContextView
from ipam.models import IPAddress, Service
from ipam.tables import InterfaceIPAddressTable, InterfaceVLANTable
from netbox.views import generic
from secrets.models import Secret
from utilities.utils import get_subquery
from . import filters, forms, tables
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine, VMInterface


#
# Cluster types
#

class ClusterTypeListView(generic.ObjectListView):
    queryset = ClusterType.objects.annotate(cluster_count=Count('clusters')).order_by(*ClusterType._meta.ordering)
    table = tables.ClusterTypeTable


class ClusterTypeEditView(generic.ObjectEditView):
    queryset = ClusterType.objects.all()
    model_form = forms.ClusterTypeForm


class ClusterTypeDeleteView(generic.ObjectDeleteView):
    queryset = ClusterType.objects.all()


class ClusterTypeBulkImportView(generic.BulkImportView):
    queryset = ClusterType.objects.all()
    model_form = forms.ClusterTypeCSVForm
    table = tables.ClusterTypeTable


class ClusterTypeBulkDeleteView(generic.BulkDeleteView):
    queryset = ClusterType.objects.annotate(cluster_count=Count('clusters')).order_by(*ClusterType._meta.ordering)
    table = tables.ClusterTypeTable


#
# Cluster groups
#

class ClusterGroupListView(generic.ObjectListView):
    queryset = ClusterGroup.objects.annotate(cluster_count=Count('clusters')).order_by(*ClusterGroup._meta.ordering)
    table = tables.ClusterGroupTable


class ClusterGroupEditView(generic.ObjectEditView):
    queryset = ClusterGroup.objects.all()
    model_form = forms.ClusterGroupForm


class ClusterGroupDeleteView(generic.ObjectDeleteView):
    queryset = ClusterGroup.objects.all()


class ClusterGroupBulkImportView(generic.BulkImportView):
    queryset = ClusterGroup.objects.all()
    model_form = forms.ClusterGroupCSVForm
    table = tables.ClusterGroupTable


class ClusterGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = ClusterGroup.objects.annotate(cluster_count=Count('clusters')).order_by(*ClusterGroup._meta.ordering)
    table = tables.ClusterGroupTable


#
# Clusters
#

class ClusterListView(generic.ObjectListView):
    permission_required = 'virtualization.view_cluster'
    queryset = Cluster.objects.annotate(
        device_count=get_subquery(Device, 'cluster'),
        vm_count=get_subquery(VirtualMachine, 'cluster')
    )
    table = tables.ClusterTable
    filterset = filters.ClusterFilterSet
    filterset_form = forms.ClusterFilterForm


class ClusterView(generic.ObjectView):
    queryset = Cluster.objects.all()

    def get(self, request, pk):
        self.queryset = self.queryset.prefetch_related(
            Prefetch('virtual_machines', queryset=VirtualMachine.objects.restrict(request.user))
        )

        cluster = get_object_or_404(self.queryset, pk=pk)
        devices = Device.objects.restrict(request.user, 'view').filter(cluster=cluster).prefetch_related(
            'site', 'rack', 'tenant', 'device_type__manufacturer'
        )
        device_table = DeviceTable(list(devices), orderable=False)
        if request.user.has_perm('virtualization.change_cluster'):
            device_table.columns.show('pk')

        return render(request, 'virtualization/cluster.html', {
            'cluster': cluster,
            'device_table': device_table,
        })


class ClusterEditView(generic.ObjectEditView):
    template_name = 'virtualization/cluster_edit.html'
    queryset = Cluster.objects.all()
    model_form = forms.ClusterForm


class ClusterDeleteView(generic.ObjectDeleteView):
    queryset = Cluster.objects.all()


class ClusterBulkImportView(generic.BulkImportView):
    queryset = Cluster.objects.all()
    model_form = forms.ClusterCSVForm
    table = tables.ClusterTable


class ClusterBulkEditView(generic.BulkEditView):
    queryset = Cluster.objects.prefetch_related('type', 'group', 'site')
    filterset = filters.ClusterFilterSet
    table = tables.ClusterTable
    form = forms.ClusterBulkEditForm


class ClusterBulkDeleteView(generic.BulkDeleteView):
    queryset = Cluster.objects.prefetch_related('type', 'group', 'site')
    filterset = filters.ClusterFilterSet
    table = tables.ClusterTable


class ClusterAddDevicesView(generic.ObjectEditView):
    queryset = Cluster.objects.all()
    form = forms.ClusterAddDevicesForm
    template_name = 'virtualization/cluster_add_devices.html'

    def get(self, request, pk):
        cluster = get_object_or_404(self.queryset, pk=pk)
        form = self.form(cluster, initial=request.GET)

        return render(request, self.template_name, {
            'cluster': cluster,
            'form': form,
            'return_url': reverse('virtualization:cluster', kwargs={'pk': pk}),
        })

    def post(self, request, pk):
        cluster = get_object_or_404(self.queryset, pk=pk)
        form = self.form(cluster, request.POST)

        if form.is_valid():

            device_pks = form.cleaned_data['devices']
            with transaction.atomic():

                # Assign the selected Devices to the Cluster
                for device in Device.objects.filter(pk__in=device_pks):
                    device.cluster = cluster
                    device.save()

            messages.success(request, "Added {} devices to cluster {}".format(
                len(device_pks), cluster
            ))
            return redirect(cluster.get_absolute_url())

        return render(request, self.template_name, {
            'cluster': cluster,
            'form': form,
            'return_url': cluster.get_absolute_url(),
        })


class ClusterRemoveDevicesView(generic.ObjectEditView):
    queryset = Cluster.objects.all()
    form = forms.ClusterRemoveDevicesForm
    template_name = 'utilities/obj_bulk_remove.html'

    def post(self, request, pk):

        cluster = get_object_or_404(self.queryset, pk=pk)

        if '_confirm' in request.POST:
            form = self.form(request.POST)
            if form.is_valid():

                device_pks = form.cleaned_data['pk']
                with transaction.atomic():

                    # Remove the selected Devices from the Cluster
                    for device in Device.objects.filter(pk__in=device_pks):
                        device.cluster = None
                        device.save()

                messages.success(request, "Removed {} devices from cluster {}".format(
                    len(device_pks), cluster
                ))
                return redirect(cluster.get_absolute_url())

        else:
            form = self.form(initial={'pk': request.POST.getlist('pk')})

        selected_objects = Device.objects.filter(pk__in=form.initial['pk'])
        device_table = DeviceTable(list(selected_objects), orderable=False)

        return render(request, self.template_name, {
            'form': form,
            'parent_obj': cluster,
            'table': device_table,
            'obj_type_plural': 'devices',
            'return_url': cluster.get_absolute_url(),
        })


#
# Virtual machines
#

class VirtualMachineListView(generic.ObjectListView):
    queryset = VirtualMachine.objects.all()
    filterset = filters.VirtualMachineFilterSet
    filterset_form = forms.VirtualMachineFilterForm
    table = tables.VirtualMachineDetailTable
    template_name = 'virtualization/virtualmachine_list.html'


class VirtualMachineView(generic.ObjectView):
    queryset = VirtualMachine.objects.prefetch_related('tenant__group')

    def get(self, request, pk):
        virtualmachine = get_object_or_404(self.queryset, pk=pk)

        # Interfaces
        vminterfaces = VMInterface.objects.restrict(request.user, 'view').filter(
            virtual_machine=virtualmachine
        ).prefetch_related(
            Prefetch('ip_addresses', queryset=IPAddress.objects.restrict(request.user))
        )
        vminterface_table = tables.VirtualMachineVMInterfaceTable(vminterfaces, orderable=False)
        if request.user.has_perm('virtualization.change_vminterface') or \
                request.user.has_perm('virtualization.delete_vminterface'):
            vminterface_table.columns.show('pk')

        # Services
        services = Service.objects.restrict(request.user, 'view').filter(
            virtual_machine=virtualmachine
        ).prefetch_related(
            Prefetch('ipaddresses', queryset=IPAddress.objects.restrict(request.user))
        )

        # Secrets
        secrets = Secret.objects.restrict(request.user, 'view').filter(virtual_machine=virtualmachine)

        return render(request, 'virtualization/virtualmachine.html', {
            'virtualmachine': virtualmachine,
            'vminterface_table': vminterface_table,
            'services': services,
            'secrets': secrets,
        })


class VirtualMachineConfigContextView(ObjectConfigContextView):
    queryset = VirtualMachine.objects.annotate_config_context_data()
    base_template = 'virtualization/virtualmachine.html'


class VirtualMachineEditView(generic.ObjectEditView):
    queryset = VirtualMachine.objects.all()
    model_form = forms.VirtualMachineForm
    template_name = 'virtualization/virtualmachine_edit.html'


class VirtualMachineDeleteView(generic.ObjectDeleteView):
    queryset = VirtualMachine.objects.all()


class VirtualMachineBulkImportView(generic.BulkImportView):
    queryset = VirtualMachine.objects.all()
    model_form = forms.VirtualMachineCSVForm
    table = tables.VirtualMachineTable


class VirtualMachineBulkEditView(generic.BulkEditView):
    queryset = VirtualMachine.objects.prefetch_related('cluster', 'tenant', 'role')
    filterset = filters.VirtualMachineFilterSet
    table = tables.VirtualMachineTable
    form = forms.VirtualMachineBulkEditForm


class VirtualMachineBulkDeleteView(generic.BulkDeleteView):
    queryset = VirtualMachine.objects.prefetch_related('cluster', 'tenant', 'role')
    filterset = filters.VirtualMachineFilterSet
    table = tables.VirtualMachineTable


#
# VM interfaces
#

class VMInterfaceListView(generic.ObjectListView):
    queryset = VMInterface.objects.all()
    filterset = filters.VMInterfaceFilterSet
    filterset_form = forms.VMInterfaceFilterForm
    table = tables.VMInterfaceTable
    action_buttons = ('export',)


class VMInterfaceView(generic.ObjectView):
    queryset = VMInterface.objects.all()

    def get(self, request, pk):

        vminterface = get_object_or_404(self.queryset, pk=pk)

        # Get assigned IP addresses
        ipaddress_table = InterfaceIPAddressTable(
            data=vminterface.ip_addresses.restrict(request.user, 'view').prefetch_related('vrf', 'tenant'),
            orderable=False
        )

        # Get assigned VLANs and annotate whether each is tagged or untagged
        vlans = []
        if vminterface.untagged_vlan is not None:
            vlans.append(vminterface.untagged_vlan)
            vlans[0].tagged = False
        for vlan in vminterface.tagged_vlans.restrict(request.user).prefetch_related('site', 'group', 'tenant', 'role'):
            vlan.tagged = True
            vlans.append(vlan)
        vlan_table = InterfaceVLANTable(
            interface=vminterface,
            data=vlans,
            orderable=False
        )

        return render(request, 'virtualization/vminterface.html', {
            'vminterface': vminterface,
            'ipaddress_table': ipaddress_table,
            'vlan_table': vlan_table,
        })


# TODO: This should not use ComponentCreateView
class VMInterfaceCreateView(generic.ComponentCreateView):
    queryset = VMInterface.objects.all()
    form = forms.VMInterfaceCreateForm
    model_form = forms.VMInterfaceForm
    template_name = 'virtualization/virtualmachine_component_add.html'


class VMInterfaceEditView(generic.ObjectEditView):
    queryset = VMInterface.objects.all()
    model_form = forms.VMInterfaceForm
    template_name = 'virtualization/vminterface_edit.html'


class VMInterfaceDeleteView(generic.ObjectDeleteView):
    queryset = VMInterface.objects.all()


class VMInterfaceBulkImportView(generic.BulkImportView):
    queryset = VMInterface.objects.all()
    model_form = forms.VMInterfaceCSVForm
    table = tables.VMInterfaceTable


class VMInterfaceBulkEditView(generic.BulkEditView):
    queryset = VMInterface.objects.all()
    table = tables.VMInterfaceTable
    form = forms.VMInterfaceBulkEditForm


class VMInterfaceBulkRenameView(generic.BulkRenameView):
    queryset = VMInterface.objects.all()
    form = forms.VMInterfaceBulkRenameForm


class VMInterfaceBulkDeleteView(generic.BulkDeleteView):
    queryset = VMInterface.objects.all()
    table = tables.VMInterfaceTable


#
# Bulk Device component creation
#

class VirtualMachineBulkAddInterfaceView(generic.BulkComponentCreateView):
    parent_model = VirtualMachine
    parent_field = 'virtual_machine'
    form = forms.VMInterfaceBulkCreateForm
    queryset = VMInterface.objects.all()
    model_form = forms.VMInterfaceForm
    filterset = filters.VirtualMachineFilterSet
    table = tables.VirtualMachineTable
