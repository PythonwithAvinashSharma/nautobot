import django_tables2 as tables
from django_tables2.utils import Accessor

from dcim.models import PowerFeed, PowerPanel
from utilities.tables import BaseTable, ChoiceFieldColumn, LinkedCountColumn, TagColumn, ToggleColumn
from .template_code import POWERFEED_CABLE, POWERFEED_CABLETERMINATION

__all__ = (
    'PowerFeedTable',
    'PowerPanelTable',
)


#
# Power panels
#

class PowerPanelTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    site = tables.LinkColumn(
        viewname='dcim:site',
        args=[Accessor('site__slug')]
    )
    powerfeed_count = LinkedCountColumn(
        viewname='dcim:powerfeed_list',
        url_params={'power_panel_id': 'pk'},
        verbose_name='Feeds'
    )
    tags = TagColumn(
        url_name='dcim:powerpanel_list'
    )

    class Meta(BaseTable.Meta):
        model = PowerPanel
        fields = ('pk', 'name', 'site', 'rack_group', 'powerfeed_count', 'tags')
        default_columns = ('pk', 'name', 'site', 'rack_group', 'powerfeed_count')


#
# Power feeds
#

class PowerFeedTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn()
    power_panel = tables.Column(
        linkify=True
    )
    rack = tables.Column(
        linkify=True
    )
    status = ChoiceFieldColumn()
    type = ChoiceFieldColumn()
    max_utilization = tables.TemplateColumn(
        template_code="{{ value }}%"
    )
    cable = tables.TemplateColumn(
        template_code=POWERFEED_CABLE,
        orderable=False
    )
    connection = tables.TemplateColumn(
        accessor='get_cable_peer',
        template_code=POWERFEED_CABLETERMINATION,
        orderable=False
    )
    available_power = tables.Column(
        verbose_name='Available power (VA)'
    )
    tags = TagColumn(
        url_name='dcim:powerfeed_list'
    )

    class Meta(BaseTable.Meta):
        model = PowerFeed
        fields = (
            'pk', 'name', 'power_panel', 'rack', 'status', 'type', 'supply', 'voltage', 'amperage', 'phase',
            'max_utilization', 'cable', 'connection', 'available_power', 'tags',
        )
        default_columns = (
            'pk', 'name', 'power_panel', 'rack', 'status', 'type', 'supply', 'voltage', 'amperage', 'phase', 'cable',
            'connection',
        )
