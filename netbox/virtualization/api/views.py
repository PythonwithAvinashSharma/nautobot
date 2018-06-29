from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response

from dcim.models import Interface
from extras.api.views import CustomFieldModelViewSet
from utilities.api import FieldChoicesViewSet, ModelViewSet
from virtualization import filters
from virtualization.models import Cluster, ClusterGroup, ClusterType, VirtualMachine
from . import serializers


#
# Field choices
#

class VirtualizationFieldChoicesViewSet(FieldChoicesViewSet):
    fields = (
        (VirtualMachine, ['status']),
    )


#
# Clusters
#

class ClusterTypeViewSet(ModelViewSet):
    queryset = ClusterType.objects.all()
    serializer_class = serializers.ClusterTypeSerializer
    filter_class = filters.ClusterTypeFilter


class ClusterGroupViewSet(ModelViewSet):
    queryset = ClusterGroup.objects.all()
    serializer_class = serializers.ClusterGroupSerializer
    filter_class = filters.ClusterGroupFilter


class ClusterViewSet(CustomFieldModelViewSet):
    queryset = Cluster.objects.select_related('type', 'group')
    serializer_class = serializers.ClusterSerializer
    filter_class = filters.ClusterFilter


#
# Virtual machines
#

class VirtualMachineViewSet(CustomFieldModelViewSet):
    queryset = VirtualMachine.objects.all()
    serializer_class = serializers.VirtualMachineSerializer
    filter_class = filters.VirtualMachineFilter

    @action(detail=True, url_path='config-context')
    def config_context(self, request, pk):
        device = get_object_or_404(VirtualMachine, pk=pk)
        return Response(device.get_config_context())


class InterfaceViewSet(ModelViewSet):
    queryset = Interface.objects.filter(virtual_machine__isnull=False).select_related('virtual_machine')
    serializer_class = serializers.InterfaceSerializer
    filter_class = filters.InterfaceFilter
