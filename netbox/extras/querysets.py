from collections import OrderedDict

from django.contrib.postgres.aggregates import JSONBAgg
from django.db.models import OuterRef, Subquery, Q, QuerySet

from utilities.query_functions import EmptyGroupByJSONBAgg
from utilities.querysets import RestrictedQuerySet


class CustomFieldQueryset:
    """
    Annotate custom fields on objects within a QuerySet.
    """
    def __init__(self, queryset, custom_fields):
        self.queryset = queryset
        self.model = queryset.model
        self.custom_fields = custom_fields

    def __iter__(self):
        for obj in self.queryset:
            values_dict = {cfv.field_id: cfv.value for cfv in obj.custom_field_values.all()}
            obj.custom_fields = OrderedDict([(field, values_dict.get(field.pk)) for field in self.custom_fields])
            yield obj


class ConfigContextQuerySet(RestrictedQuerySet):

    def get_for_object(self, obj, aggregate_data=False):
        """
        Return all applicable ConfigContexts for a given object. Only active ConfigContexts will be included.

        Args:
          aggregate_data: If True, use the JSONBAgg aggregate function to return only the list of JSON data objects
        """

        # `device_role` for Device; `role` for VirtualMachine
        role = getattr(obj, 'device_role', None) or obj.role

        # Virtualization cluster for VirtualMachine
        cluster = getattr(obj, 'cluster', None)
        cluster_group = getattr(cluster, 'group', None)

        # Get the group of the assigned tenant, if any
        tenant_group = obj.tenant.group if obj.tenant else None

        # Match against the directly assigned region as well as any parent regions.
        region = getattr(obj.site, 'region', None)
        if region:
            regions = region.get_ancestors(include_self=True)
        else:
            regions = []

        queryset = self.filter(
            Q(regions__in=regions) | Q(regions=None),
            Q(sites=obj.site) | Q(sites=None),
            Q(roles=role) | Q(roles=None),
            Q(platforms=obj.platform) | Q(platforms=None),
            Q(cluster_groups=cluster_group) | Q(cluster_groups=None),
            Q(clusters=cluster) | Q(clusters=None),
            Q(tenant_groups=tenant_group) | Q(tenant_groups=None),
            Q(tenants=obj.tenant) | Q(tenants=None),
            Q(tags__slug__in=obj.tags.slugs()) | Q(tags=None),
            is_active=True,
        ).order_by('weight', 'name')

        if aggregate_data:
            queryset = queryset.aggregate(config_context_data=JSONBAgg('data'))['config_context_data']

        return queryset


class ConfigContextModelQuerySet(RestrictedQuerySet):
    """
    QuerySet manager used by models which support ConfigContext (device and virtual machine).

    Includes a method which appends an annotation of aggregated config context JSON data objects. This is
    implemented as a subquery which performs all the joins necessary to filter relevant config context objects.
    This offers a substantial performance gain over ConfigContextQuerySet.get_for_object() when dealing with
    multiple objects.

    This allows the annotation to be entirely optional.
    """

    def annotate_config_context_data(self):
        """
        Attach the subquery annotation to the base queryset
        """
        from extras.models import ConfigContext
        return self.annotate(
            config_context_data=Subquery(
                ConfigContext.objects.filter(
                    self._get_config_context_filters()
                ).order_by(
                    'weight',
                    'name'
                ).annotate(
                    _data=EmptyGroupByJSONBAgg('data')
                ).values("_data")
            )
        )

    def _get_config_context_filters(self):
        # Construct the set of Q objects for the specific object types
        base_query = Q(
            Q(platforms=OuterRef('platform')) | Q(platforms=None),
            Q(tenant_groups=OuterRef('tenant__group')) | Q(tenant_groups=None),
            Q(tenants=OuterRef('tenant')) | Q(tenants=None),
            Q(tags=OuterRef('tags')) | Q(tags=None),
            is_active=True,
        )

        if self.model._meta.model_name == 'device':
            base_query.add((Q(roles=OuterRef('device_role')) | Q(roles=None)), Q.AND)
            base_query.add(
                (Q(
                    regions__tree_id=OuterRef('site__region__tree_id'),
                    regions__level__lte=OuterRef('site__region__level'),
                    regions__lft__lte=OuterRef('site__region__lft'),
                    regions__rght__gte=OuterRef('site__region__rght'),
                ) | Q(regions=None)),
                Q.AND
            )
            base_query.add((Q(sites=OuterRef('site')) | Q(sites=None)), Q.AND)

        elif self.model._meta.model_name == 'virtualmachine':
            base_query.add((Q(roles=OuterRef('role')) | Q(roles=None)), Q.AND)
            base_query.add((Q(cluster_groups=OuterRef('cluster__group')) | Q(cluster_groups=None)), Q.AND)
            base_query.add((Q(clusters=OuterRef('cluster')) | Q(clusters=None)), Q.AND)
            base_query.add(
                (Q(
                    regions__tree_id=OuterRef('cluster__site__region__tree_id'),
                    regions__level__lte=OuterRef('cluster__site__region__level'),
                    regions__lft__lte=OuterRef('cluster__site__region__lft'),
                    regions__rght__gte=OuterRef('cluster__site__region__rght'),
                ) | Q(regions=None)),
                Q.AND
            )
            base_query.add((Q(sites=OuterRef('cluster__site')) | Q(sites=None)), Q.AND)

        return base_query
