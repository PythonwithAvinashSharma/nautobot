# Models which support custom fields
CUSTOMFIELD_MODELS = [
    'circuits.circuit',
    'circuits.provider',
    'dcim.device',
    'dcim.devicetype',
    'dcim.powerfeed',
    'dcim.rack',
    'dcim.site',
    'ipam.aggregate',
    'ipam.ipaddress',
    'ipam.prefix',
    'ipam.service',
    'ipam.vlan',
    'ipam.vrf',
    'secrets.secret',
    'tenancy.tenant',
    'virtualization.cluster',
    'virtualization.virtualmachine',
]

# Custom links
CUSTOMLINK_MODELS = [
    'circuits.circuit',
    'circuits.provider',
    'dcim.cable',
    'dcim.device',
    'dcim.devicetype',
    'dcim.powerpanel',
    'dcim.powerfeed',
    'dcim.rack',
    'dcim.site',
    'ipam.aggregate',
    'ipam.ipaddress',
    'ipam.prefix',
    'ipam.service',
    'ipam.vlan',
    'ipam.vrf',
    'secrets.secret',
    'tenancy.tenant',
    'virtualization.cluster',
    'virtualization.virtualmachine',
]

# Graph types
GRAPH_TYPE_INTERFACE = 100
GRAPH_TYPE_DEVICE = 150
GRAPH_TYPE_PROVIDER = 200
GRAPH_TYPE_SITE = 300
GRAPH_TYPE_CHOICES = (
    (GRAPH_TYPE_INTERFACE, 'Interface'),
    (GRAPH_TYPE_DEVICE, 'Device'),
    (GRAPH_TYPE_PROVIDER, 'Provider'),
    (GRAPH_TYPE_SITE, 'Site'),
)

# Models which support export templates
EXPORTTEMPLATE_MODELS = [
    'circuits.circuit',
    'circuits.provider',
    'dcim.cable',
    'dcim.consoleport',
    'dcim.device',
    'dcim.devicetype',
    'dcim.interface',
    'dcim.inventoryitem',
    'dcim.manufacturer',
    'dcim.powerpanel',
    'dcim.powerport',
    'dcim.powerfeed',
    'dcim.rack',
    'dcim.rackgroup',
    'dcim.region',
    'dcim.site',
    'dcim.virtualchassis',
    'ipam.aggregate',
    'ipam.ipaddress',
    'ipam.prefix',
    'ipam.service',
    'ipam.vlan',
    'ipam.vrf',
    'secrets.secret',
    'tenancy.tenant',
    'virtualization.cluster',
    'virtualization.virtualmachine',
]

# ExportTemplate language choices
TEMPLATE_LANGUAGE_DJANGO = 10
TEMPLATE_LANGUAGE_JINJA2 = 20
TEMPLATE_LANGUAGE_CHOICES = (
    (TEMPLATE_LANGUAGE_DJANGO, 'Django'),
    (TEMPLATE_LANGUAGE_JINJA2, 'Jinja2'),
)

# User action types
ACTION_CREATE = 1
ACTION_IMPORT = 2
ACTION_EDIT = 3
ACTION_BULK_EDIT = 4
ACTION_DELETE = 5
ACTION_BULK_DELETE = 6
ACTION_BULK_CREATE = 7
ACTION_CHOICES = (
    (ACTION_CREATE, 'created'),
    (ACTION_BULK_CREATE, 'bulk created'),
    (ACTION_IMPORT, 'imported'),
    (ACTION_EDIT, 'modified'),
    (ACTION_BULK_EDIT, 'bulk edited'),
    (ACTION_DELETE, 'deleted'),
    (ACTION_BULK_DELETE, 'bulk deleted'),
)

# Report logging levels
LOG_DEFAULT = 0
LOG_SUCCESS = 10
LOG_INFO = 20
LOG_WARNING = 30
LOG_FAILURE = 40
LOG_LEVEL_CODES = {
    LOG_DEFAULT: 'default',
    LOG_SUCCESS: 'success',
    LOG_INFO: 'info',
    LOG_WARNING: 'warning',
    LOG_FAILURE: 'failure',
}

# webhook content types
WEBHOOK_CT_JSON = 1
WEBHOOK_CT_X_WWW_FORM_ENCODED = 2
WEBHOOK_CT_CHOICES = (
    (WEBHOOK_CT_JSON, 'application/json'),
    (WEBHOOK_CT_X_WWW_FORM_ENCODED, 'application/x-www-form-urlencoded'),
)

# Models which support registered webhooks
WEBHOOK_MODELS = [
    'circuits.circuit',
    'circuits.provider',
    'dcim.cable',
    'dcim.consoleport',
    'dcim.consoleserverport',
    'dcim.device',
    'dcim.devicebay',
    'dcim.devicetype',
    'dcim.interface',
    'dcim.inventoryitem',
    'dcim.frontport',
    'dcim.manufacturer',
    'dcim.poweroutlet',
    'dcim.powerpanel',
    'dcim.powerport',
    'dcim.powerfeed',
    'dcim.rack',
    'dcim.rearport',
    'dcim.region',
    'dcim.site',
    'dcim.virtualchassis',
    'ipam.aggregate',
    'ipam.ipaddress',
    'ipam.prefix',
    'ipam.service',
    'ipam.vlan',
    'ipam.vrf',
    'secrets.secret',
    'tenancy.tenant',
    'virtualization.cluster',
    'virtualization.virtualmachine',
]
