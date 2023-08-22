import graphene
import graphene_django_optimizer as gql_optimizer

from nautobot.core.graphql.types import OptimizedNautobotObjectType
from nautobot.extras.models import DynamicGroup
from nautobot.virtualization.filters import ClusterFilterSet, VirtualMachineFilterSet, VMInterfaceFilterSet
from nautobot.virtualization.models import Cluster, VirtualMachine, VMInterface


class ClusterType(OptimizedNautobotObjectType):
    """GraphQL type object for Cluster model."""

    dynamic_groups = graphene.List("nautobot.extras.graphql.types.DynamicGroupType")

    class Meta:
        model = Cluster
        filterset_class = ClusterFilterSet

    def resolve_dynamic_groups(self, args):
        return DynamicGroup.objects.get_for_object(self, use_cache=True)


class VirtualMachineType(OptimizedNautobotObjectType):
    """GraphQL type object for VirtualMachine model."""

    dynamic_groups = graphene.List("nautobot.extras.graphql.types.DynamicGroupType")

    class Meta:
        model = VirtualMachine
        filterset_class = VirtualMachineFilterSet

    def resolve_dynamic_groups(self, args):
        return DynamicGroup.objects.get_for_object(self, use_cache=True)


class VMInterfaceType(OptimizedNautobotObjectType):
    """GraphQL type object for VMInterface model."""

    class Meta:
        model = VMInterface
        filterset_class = VMInterfaceFilterSet
        exclude = ["_name"]

    ip_addresses = graphene.List("nautobot.ipam.graphql.types.IPAddressType")

    # VMInterface.ip_addresses is the reverse side of a GenericRelation that cannot be auto-optimized.
    # See: https://github.com/tfoxy/graphene-django-optimizer#advanced-usage
    @gql_optimizer.resolver_hints(
        model_field="ip_addresses",
    )
    def resolve_ip_addresses(self, args):
        return self.ip_addresses.all()
