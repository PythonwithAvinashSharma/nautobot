from django.conf.urls import url

from extras.views import ObjectChangeLogView, ImageAttachmentEditView
from ipam.views import ServiceCreateView
from secrets.views import secret_add
from utilities.urls import cached
from . import views
from .models import (
    Cable, ConsolePort, ConsoleServerPort, Device, DeviceRole, DeviceType, FrontPort, Interface, Manufacturer, Platform,
    PowerFeed, PowerPanel, PowerPort, PowerOutlet, Rack, RackGroup, RackReservation, RackRole, RearPort, Region, Site,
    VirtualChassis,
)

app_name = 'dcim'
urlpatterns = [

    # Regions
    url(r'^regions/$', cached(views.RegionListView.as_view()), name='region_list'),
    url(r'^regions/add/$', cached(views.RegionCreateView.as_view()), name='region_add'),
    url(r'^regions/import/$', views.RegionBulkImportView.as_view(), name='region_import'),
    url(r'^regions/delete/$', views.RegionBulkDeleteView.as_view(), name='region_bulk_delete'),
    url(r'^regions/(?P<pk>\d+)/edit/$', views.RegionEditView.as_view(), name='region_edit'),
    url(r'^regions/(?P<pk>\d+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='region_changelog', kwargs={'model': Region}),

    # Sites
    url(r'^sites/$', cached(views.SiteListView.as_view()), name='site_list'),
    url(r'^sites/add/$', cached(views.SiteCreateView.as_view()), name='site_add'),
    url(r'^sites/import/$', views.SiteBulkImportView.as_view(), name='site_import'),
    url(r'^sites/edit/$', views.SiteBulkEditView.as_view(), name='site_bulk_edit'),
    url(r'^sites/(?P<slug>[\w-]+)/$', cached(views.SiteView.as_view()), name='site'),
    url(r'^sites/(?P<slug>[\w-]+)/edit/$', views.SiteEditView.as_view(), name='site_edit'),
    url(r'^sites/(?P<slug>[\w-]+)/delete/$', views.SiteDeleteView.as_view(), name='site_delete'),
    url(r'^sites/(?P<slug>[\w-]+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='site_changelog', kwargs={'model': Site}),
    url(r'^sites/(?P<object_id>\d+)/images/add/$', cached(ImageAttachmentEditView.as_view()), name='site_add_image', kwargs={'model': Site}),

    # Rack groups
    url(r'^rack-groups/$', cached(views.RackGroupListView.as_view()), name='rackgroup_list'),
    url(r'^rack-groups/add/$', cached(views.RackGroupCreateView.as_view()), name='rackgroup_add'),
    url(r'^rack-groups/import/$', views.RackGroupBulkImportView.as_view(), name='rackgroup_import'),
    url(r'^rack-groups/delete/$', views.RackGroupBulkDeleteView.as_view(), name='rackgroup_bulk_delete'),
    url(r'^rack-groups/(?P<pk>\d+)/edit/$', views.RackGroupEditView.as_view(), name='rackgroup_edit'),
    url(r'^rack-groups/(?P<pk>\d+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='rackgroup_changelog', kwargs={'model': RackGroup}),

    # Rack roles
    url(r'^rack-roles/$', cached(views.RackRoleListView.as_view()), name='rackrole_list'),
    url(r'^rack-roles/add/$', cached(views.RackRoleCreateView.as_view()), name='rackrole_add'),
    url(r'^rack-roles/import/$', views.RackRoleBulkImportView.as_view(), name='rackrole_import'),
    url(r'^rack-roles/delete/$', views.RackRoleBulkDeleteView.as_view(), name='rackrole_bulk_delete'),
    url(r'^rack-roles/(?P<pk>\d+)/edit/$', views.RackRoleEditView.as_view(), name='rackrole_edit'),
    url(r'^rack-roles/(?P<pk>\d+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='rackrole_changelog', kwargs={'model': RackRole}),

    # Rack reservations
    url(r'^rack-reservations/$', cached(views.RackReservationListView.as_view()), name='rackreservation_list'),
    url(r'^rack-reservations/edit/$', views.RackReservationBulkEditView.as_view(), name='rackreservation_bulk_edit'),
    url(r'^rack-reservations/delete/$', views.RackReservationBulkDeleteView.as_view(), name='rackreservation_bulk_delete'),
    url(r'^rack-reservations/(?P<pk>\d+)/edit/$', views.RackReservationEditView.as_view(), name='rackreservation_edit'),
    url(r'^rack-reservations/(?P<pk>\d+)/delete/$', views.RackReservationDeleteView.as_view(), name='rackreservation_delete'),
    url(r'^rack-reservations/(?P<pk>\d+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='rackreservation_changelog', kwargs={'model': RackReservation}),

    # Racks
    url(r'^racks/$', cached(views.RackListView.as_view()), name='rack_list'),
    url(r'^rack-elevations/$', cached(views.RackElevationListView.as_view()), name='rack_elevation_list'),
    url(r'^racks/add/$', cached(views.RackEditView.as_view()), name='rack_add'),
    url(r'^racks/import/$', views.RackBulkImportView.as_view(), name='rack_import'),
    url(r'^racks/edit/$', views.RackBulkEditView.as_view(), name='rack_bulk_edit'),
    url(r'^racks/delete/$', views.RackBulkDeleteView.as_view(), name='rack_bulk_delete'),
    url(r'^racks/(?P<pk>\d+)/$', cached(views.RackView.as_view()), name='rack'),
    url(r'^racks/(?P<pk>\d+)/edit/$', views.RackEditView.as_view(), name='rack_edit'),
    url(r'^racks/(?P<pk>\d+)/delete/$', views.RackDeleteView.as_view(), name='rack_delete'),
    url(r'^racks/(?P<pk>\d+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='rack_changelog', kwargs={'model': Rack}),
    url(r'^racks/(?P<rack>\d+)/reservations/add/$', cached(views.RackReservationCreateView.as_view()), name='rack_add_reservation'),
    url(r'^racks/(?P<object_id>\d+)/images/add/$', cached(ImageAttachmentEditView.as_view()), name='rack_add_image', kwargs={'model': Rack}),

    # Manufacturers
    url(r'^manufacturers/$', cached(views.ManufacturerListView.as_view()), name='manufacturer_list'),
    url(r'^manufacturers/add/$', cached(views.ManufacturerCreateView.as_view()), name='manufacturer_add'),
    url(r'^manufacturers/import/$', views.ManufacturerBulkImportView.as_view(), name='manufacturer_import'),
    url(r'^manufacturers/delete/$', views.ManufacturerBulkDeleteView.as_view(), name='manufacturer_bulk_delete'),
    url(r'^manufacturers/(?P<slug>[\w-]+)/edit/$', views.ManufacturerEditView.as_view(), name='manufacturer_edit'),
    url(r'^manufacturers/(?P<slug>[\w-]+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='manufacturer_changelog', kwargs={'model': Manufacturer}),

    # Device types
    url(r'^device-types/$', cached(views.DeviceTypeListView.as_view()), name='devicetype_list'),
    url(r'^device-types/add/$', cached(views.DeviceTypeCreateView.as_view()), name='devicetype_add'),
    url(r'^device-types/import/$', views.DeviceTypeBulkImportView.as_view(), name='devicetype_import'),
    url(r'^device-types/edit/$', views.DeviceTypeBulkEditView.as_view(), name='devicetype_bulk_edit'),
    url(r'^device-types/delete/$', views.DeviceTypeBulkDeleteView.as_view(), name='devicetype_bulk_delete'),
    url(r'^device-types/(?P<pk>\d+)/$', cached(views.DeviceTypeView.as_view()), name='devicetype'),
    url(r'^device-types/(?P<pk>\d+)/edit/$', views.DeviceTypeEditView.as_view(), name='devicetype_edit'),
    url(r'^device-types/(?P<pk>\d+)/delete/$', views.DeviceTypeDeleteView.as_view(), name='devicetype_delete'),
    url(r'^device-types/(?P<pk>\d+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='devicetype_changelog', kwargs={'model': DeviceType}),

    # Console port templates
    url(r'^device-types/(?P<pk>\d+)/console-ports/add/$', cached(views.ConsolePortTemplateCreateView.as_view()), name='devicetype_add_consoleport'),
    url(r'^device-types/(?P<pk>\d+)/console-ports/delete/$', views.ConsolePortTemplateBulkDeleteView.as_view(), name='devicetype_delete_consoleport'),

    # Console server port templates
    url(r'^device-types/(?P<pk>\d+)/console-server-ports/add/$', cached(views.ConsoleServerPortTemplateCreateView.as_view()), name='devicetype_add_consoleserverport'),
    url(r'^device-types/(?P<pk>\d+)/console-server-ports/delete/$', views.ConsoleServerPortTemplateBulkDeleteView.as_view(), name='devicetype_delete_consoleserverport'),

    # Power port templates
    url(r'^device-types/(?P<pk>\d+)/power-ports/add/$', cached(views.PowerPortTemplateCreateView.as_view()), name='devicetype_add_powerport'),
    url(r'^device-types/(?P<pk>\d+)/power-ports/delete/$', views.PowerPortTemplateBulkDeleteView.as_view(), name='devicetype_delete_powerport'),

    # Power outlet templates
    url(r'^device-types/(?P<pk>\d+)/power-outlets/add/$', cached(views.PowerOutletTemplateCreateView.as_view()), name='devicetype_add_poweroutlet'),
    url(r'^device-types/(?P<pk>\d+)/power-outlets/delete/$', views.PowerOutletTemplateBulkDeleteView.as_view(), name='devicetype_delete_poweroutlet'),

    # Interface templates
    url(r'^device-types/(?P<pk>\d+)/interfaces/add/$', cached(views.InterfaceTemplateCreateView.as_view()), name='devicetype_add_interface'),
    url(r'^device-types/(?P<pk>\d+)/interfaces/edit/$', views.InterfaceTemplateBulkEditView.as_view(), name='devicetype_bulkedit_interface'),
    url(r'^device-types/(?P<pk>\d+)/interfaces/delete/$', views.InterfaceTemplateBulkDeleteView.as_view(), name='devicetype_delete_interface'),

    # Front port templates
    url(r'^device-types/(?P<pk>\d+)/front-ports/add/$', cached(views.FrontPortTemplateCreateView.as_view()), name='devicetype_add_frontport'),
    url(r'^device-types/(?P<pk>\d+)/front-ports/delete/$', views.FrontPortTemplateBulkDeleteView.as_view(), name='devicetype_delete_frontport'),

    # Rear port templates
    url(r'^device-types/(?P<pk>\d+)/rear-ports/add/$', cached(views.RearPortTemplateCreateView.as_view()), name='devicetype_add_rearport'),
    url(r'^device-types/(?P<pk>\d+)/rear-ports/delete/$', views.RearPortTemplateBulkDeleteView.as_view(), name='devicetype_delete_rearport'),

    # Device bay templates
    url(r'^device-types/(?P<pk>\d+)/device-bays/add/$', cached(views.DeviceBayTemplateCreateView.as_view()), name='devicetype_add_devicebay'),
    url(r'^device-types/(?P<pk>\d+)/device-bays/delete/$', views.DeviceBayTemplateBulkDeleteView.as_view(), name='devicetype_delete_devicebay'),

    # Device roles
    url(r'^device-roles/$', cached(views.DeviceRoleListView.as_view()), name='devicerole_list'),
    url(r'^device-roles/add/$', cached(views.DeviceRoleCreateView.as_view()), name='devicerole_add'),
    url(r'^device-roles/import/$', views.DeviceRoleBulkImportView.as_view(), name='devicerole_import'),
    url(r'^device-roles/delete/$', views.DeviceRoleBulkDeleteView.as_view(), name='devicerole_bulk_delete'),
    url(r'^device-roles/(?P<slug>[\w-]+)/edit/$', views.DeviceRoleEditView.as_view(), name='devicerole_edit'),
    url(r'^device-roles/(?P<slug>[\w-]+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='devicerole_changelog', kwargs={'model': DeviceRole}),

    # Platforms
    url(r'^platforms/$', cached(views.PlatformListView.as_view()), name='platform_list'),
    url(r'^platforms/add/$', cached(views.PlatformCreateView.as_view()), name='platform_add'),
    url(r'^platforms/import/$', views.PlatformBulkImportView.as_view(), name='platform_import'),
    url(r'^platforms/delete/$', views.PlatformBulkDeleteView.as_view(), name='platform_bulk_delete'),
    url(r'^platforms/(?P<slug>[\w-]+)/edit/$', views.PlatformEditView.as_view(), name='platform_edit'),
    url(r'^platforms/(?P<slug>[\w-]+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='platform_changelog', kwargs={'model': Platform}),

    # Devices
    url(r'^devices/$', cached(views.DeviceListView.as_view()), name='device_list'),
    url(r'^devices/add/$', cached(views.DeviceCreateView.as_view()), name='device_add'),
    url(r'^devices/import/$', views.DeviceBulkImportView.as_view(), name='device_import'),
    url(r'^devices/import/child-devices/$', views.ChildDeviceBulkImportView.as_view(), name='device_import_child'),
    url(r'^devices/edit/$', views.DeviceBulkEditView.as_view(), name='device_bulk_edit'),
    url(r'^devices/delete/$', views.DeviceBulkDeleteView.as_view(), name='device_bulk_delete'),
    url(r'^devices/(?P<pk>\d+)/$', cached(views.DeviceView.as_view()), name='device'),
    url(r'^devices/(?P<pk>\d+)/edit/$', views.DeviceEditView.as_view(), name='device_edit'),
    url(r'^devices/(?P<pk>\d+)/delete/$', views.DeviceDeleteView.as_view(), name='device_delete'),
    url(r'^devices/(?P<pk>\d+)/config-context/$', cached(views.DeviceConfigContextView.as_view()), name='device_configcontext'),
    url(r'^devices/(?P<pk>\d+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='device_changelog', kwargs={'model': Device}),
    url(r'^devices/(?P<pk>\d+)/inventory/$', cached(views.DeviceInventoryView.as_view()), name='device_inventory'),
    url(r'^devices/(?P<pk>\d+)/status/$', views.DeviceStatusView.as_view(), name='device_status'),
    url(r'^devices/(?P<pk>\d+)/lldp-neighbors/$', views.DeviceLLDPNeighborsView.as_view(), name='device_lldp_neighbors'),
    url(r'^devices/(?P<pk>\d+)/config/$', views.DeviceConfigView.as_view(), name='device_config'),
    url(r'^devices/(?P<pk>\d+)/add-secret/$', secret_add, name='device_addsecret'),
    url(r'^devices/(?P<device>\d+)/services/assign/$', cached(ServiceCreateView.as_view()), name='device_service_assign'),
    url(r'^devices/(?P<object_id>\d+)/images/add/$', cached(ImageAttachmentEditView.as_view()), name='device_add_image', kwargs={'model': Device}),

    # Console ports
    url(r'^devices/console-ports/add/$', cached(views.DeviceBulkAddConsolePortView.as_view()), name='device_bulk_add_consoleport'),
    url(r'^devices/(?P<pk>\d+)/console-ports/add/$', cached(views.ConsolePortCreateView.as_view()), name='consoleport_add'),
    url(r'^devices/(?P<pk>\d+)/console-ports/delete/$', views.ConsolePortBulkDeleteView.as_view(), name='consoleport_bulk_delete'),
    url(r'^console-ports/(?P<termination_a_id>\d+)/connect/(?P<termination_b_type>[\w-]+)/$', views.CableCreateView.as_view(), name='consoleport_connect', kwargs={'termination_a_type': ConsolePort}),
    url(r'^console-ports/(?P<pk>\d+)/edit/$', views.ConsolePortEditView.as_view(), name='consoleport_edit'),
    url(r'^console-ports/(?P<pk>\d+)/delete/$', views.ConsolePortDeleteView.as_view(), name='consoleport_delete'),
    url(r'^console-ports/(?P<pk>\d+)/trace/$', cached(views.CableTraceView.as_view()), name='consoleport_trace', kwargs={'model': ConsolePort}),

    # Console server ports
    url(r'^devices/console-server-ports/add/$', cached(views.DeviceBulkAddConsoleServerPortView.as_view()), name='device_bulk_add_consoleserverport'),
    url(r'^devices/(?P<pk>\d+)/console-server-ports/add/$', cached(views.ConsoleServerPortCreateView.as_view()), name='consoleserverport_add'),
    url(r'^devices/(?P<pk>\d+)/console-server-ports/delete/$', views.ConsoleServerPortBulkDeleteView.as_view(), name='consoleserverport_bulk_delete'),
    url(r'^console-server-ports/(?P<termination_a_id>\d+)/connect/(?P<termination_b_type>[\w-]+)/$', views.CableCreateView.as_view(), name='consoleserverport_connect', kwargs={'termination_a_type': ConsoleServerPort}),
    url(r'^console-server-ports/(?P<pk>\d+)/edit/$', views.ConsoleServerPortEditView.as_view(), name='consoleserverport_edit'),
    url(r'^console-server-ports/(?P<pk>\d+)/delete/$', views.ConsoleServerPortDeleteView.as_view(), name='consoleserverport_delete'),
    url(r'^console-server-ports/(?P<pk>\d+)/trace/$', cached(views.CableTraceView.as_view()), name='consoleserverport_trace', kwargs={'model': ConsoleServerPort}),
    url(r'^console-server-ports/rename/$', cached(views.ConsoleServerPortBulkRenameView.as_view()), name='consoleserverport_bulk_rename'),
    url(r'^console-server-ports/disconnect/$', views.ConsoleServerPortBulkDisconnectView.as_view(), name='consoleserverport_bulk_disconnect'),

    # Power ports
    url(r'^devices/power-ports/add/$', cached(views.DeviceBulkAddPowerPortView.as_view()), name='device_bulk_add_powerport'),
    url(r'^devices/(?P<pk>\d+)/power-ports/add/$', cached(views.PowerPortCreateView.as_view()), name='powerport_add'),
    url(r'^devices/(?P<pk>\d+)/power-ports/delete/$', views.PowerPortBulkDeleteView.as_view(), name='powerport_bulk_delete'),
    url(r'^power-ports/(?P<termination_a_id>\d+)/connect/(?P<termination_b_type>[\w-]+)/$', views.CableCreateView.as_view(), name='powerport_connect', kwargs={'termination_a_type': PowerPort}),
    url(r'^power-ports/(?P<pk>\d+)/edit/$', views.PowerPortEditView.as_view(), name='powerport_edit'),
    url(r'^power-ports/(?P<pk>\d+)/delete/$', views.PowerPortDeleteView.as_view(), name='powerport_delete'),
    url(r'^power-ports/(?P<pk>\d+)/trace/$', cached(views.CableTraceView.as_view()), name='powerport_trace', kwargs={'model': PowerPort}),

    # Power outlets
    url(r'^devices/power-outlets/add/$', cached(views.DeviceBulkAddPowerOutletView.as_view()), name='device_bulk_add_poweroutlet'),
    url(r'^devices/(?P<pk>\d+)/power-outlets/add/$', cached(views.PowerOutletCreateView.as_view()), name='poweroutlet_add'),
    url(r'^devices/(?P<pk>\d+)/power-outlets/delete/$', views.PowerOutletBulkDeleteView.as_view(), name='poweroutlet_bulk_delete'),
    url(r'^power-outlets/(?P<termination_a_id>\d+)/connect/(?P<termination_b_type>[\w-]+)/$', views.CableCreateView.as_view(), name='poweroutlet_connect', kwargs={'termination_a_type': PowerOutlet}),
    url(r'^power-outlets/(?P<pk>\d+)/edit/$', views.PowerOutletEditView.as_view(), name='poweroutlet_edit'),
    url(r'^power-outlets/(?P<pk>\d+)/delete/$', views.PowerOutletDeleteView.as_view(), name='poweroutlet_delete'),
    url(r'^power-outlets/(?P<pk>\d+)/trace/$', cached(views.CableTraceView.as_view()), name='poweroutlet_trace', kwargs={'model': PowerOutlet}),
    url(r'^power-outlets/rename/$', cached(views.PowerOutletBulkRenameView.as_view()), name='poweroutlet_bulk_rename'),
    url(r'^power-outlets/disconnect/$', views.PowerOutletBulkDisconnectView.as_view(), name='poweroutlet_bulk_disconnect'),

    # Interfaces
    url(r'^devices/interfaces/add/$', cached(views.DeviceBulkAddInterfaceView.as_view()), name='device_bulk_add_interface'),
    url(r'^devices/(?P<pk>\d+)/interfaces/add/$', cached(views.InterfaceCreateView.as_view()), name='interface_add'),
    url(r'^devices/(?P<pk>\d+)/interfaces/edit/$', views.InterfaceBulkEditView.as_view(), name='interface_bulk_edit'),
    url(r'^devices/(?P<pk>\d+)/interfaces/delete/$', views.InterfaceBulkDeleteView.as_view(), name='interface_bulk_delete'),
    url(r'^interfaces/(?P<termination_a_id>\d+)/connect/(?P<termination_b_type>[\w-]+)/$', views.CableCreateView.as_view(), name='interface_connect', kwargs={'termination_a_type': Interface}),
    url(r'^interfaces/(?P<pk>\d+)/$', cached(views.InterfaceView.as_view()), name='interface'),
    url(r'^interfaces/(?P<pk>\d+)/edit/$', views.InterfaceEditView.as_view(), name='interface_edit'),
    url(r'^interfaces/(?P<pk>\d+)/assign-vlans/$', cached(views.InterfaceAssignVLANsView.as_view()), name='interface_assign_vlans'),
    url(r'^interfaces/(?P<pk>\d+)/delete/$', views.InterfaceDeleteView.as_view(), name='interface_delete'),
    url(r'^interfaces/(?P<pk>\d+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='interface_changelog', kwargs={'model': Interface}),
    url(r'^interfaces/(?P<pk>\d+)/trace/$', cached(views.CableTraceView.as_view()), name='interface_trace', kwargs={'model': Interface}),
    url(r'^interfaces/rename/$', cached(views.InterfaceBulkRenameView.as_view()), name='interface_bulk_rename'),
    url(r'^interfaces/disconnect/$', views.InterfaceBulkDisconnectView.as_view(), name='interface_bulk_disconnect'),

    # Front ports
    # url(r'^devices/front-ports/add/$', views.DeviceBulkAddFrontPortView.as_view(), name='device_bulk_add_frontport'),
    url(r'^devices/(?P<pk>\d+)/front-ports/add/$', cached(views.FrontPortCreateView.as_view()), name='frontport_add'),
    url(r'^devices/(?P<pk>\d+)/front-ports/edit/$', views.FrontPortBulkEditView.as_view(), name='frontport_bulk_edit'),
    url(r'^devices/(?P<pk>\d+)/front-ports/delete/$', views.FrontPortBulkDeleteView.as_view(), name='frontport_bulk_delete'),
    url(r'^front-ports/(?P<termination_a_id>\d+)/connect/(?P<termination_b_type>[\w-]+)/$', views.CableCreateView.as_view(), name='frontport_connect', kwargs={'termination_a_type': FrontPort}),
    url(r'^front-ports/(?P<pk>\d+)/edit/$', views.FrontPortEditView.as_view(), name='frontport_edit'),
    url(r'^front-ports/(?P<pk>\d+)/delete/$', views.FrontPortDeleteView.as_view(), name='frontport_delete'),
    url(r'^front-ports/(?P<pk>\d+)/trace/$', cached(views.CableTraceView.as_view()), name='frontport_trace', kwargs={'model': FrontPort}),
    url(r'^front-ports/rename/$', cached(views.FrontPortBulkRenameView.as_view()), name='frontport_bulk_rename'),
    url(r'^front-ports/disconnect/$', views.FrontPortBulkDisconnectView.as_view(), name='frontport_bulk_disconnect'),

    # Rear ports
    # url(r'^devices/rear-ports/add/$', views.DeviceBulkAddRearPortView.as_view(), name='device_bulk_add_rearport'),
    url(r'^devices/(?P<pk>\d+)/rear-ports/add/$', cached(views.RearPortCreateView.as_view()), name='rearport_add'),
    url(r'^devices/(?P<pk>\d+)/rear-ports/edit/$', views.RearPortBulkEditView.as_view(), name='rearport_bulk_edit'),
    url(r'^devices/(?P<pk>\d+)/rear-ports/delete/$', views.RearPortBulkDeleteView.as_view(), name='rearport_bulk_delete'),
    url(r'^rear-ports/(?P<termination_a_id>\d+)/connect/(?P<termination_b_type>[\w-]+)/$', views.CableCreateView.as_view(), name='rearport_connect', kwargs={'termination_a_type': RearPort}),
    url(r'^rear-ports/(?P<pk>\d+)/edit/$', views.RearPortEditView.as_view(), name='rearport_edit'),
    url(r'^rear-ports/(?P<pk>\d+)/delete/$', views.RearPortDeleteView.as_view(), name='rearport_delete'),
    url(r'^rear-ports/(?P<pk>\d+)/trace/$',cached( views.CableTraceView.as_view()), name='rearport_trace', kwargs={'model': RearPort}),
    url(r'^rear-ports/rename/$', cached(views.RearPortBulkRenameView.as_view()), name='rearport_bulk_rename'),
    url(r'^rear-ports/disconnect/$', views.RearPortBulkDisconnectView.as_view(), name='rearport_bulk_disconnect'),

    # Device bays
    url(r'^devices/device-bays/add/$', cached(views.DeviceBulkAddDeviceBayView.as_view()), name='device_bulk_add_devicebay'),
    url(r'^devices/(?P<pk>\d+)/bays/add/$', cached(views.DeviceBayCreateView.as_view()), name='devicebay_add'),
    url(r'^devices/(?P<pk>\d+)/bays/delete/$', views.DeviceBayBulkDeleteView.as_view(), name='devicebay_bulk_delete'),
    url(r'^device-bays/(?P<pk>\d+)/edit/$', views.DeviceBayEditView.as_view(), name='devicebay_edit'),
    url(r'^device-bays/(?P<pk>\d+)/delete/$', views.DeviceBayDeleteView.as_view(), name='devicebay_delete'),
    url(r'^device-bays/(?P<pk>\d+)/populate/$', views.DeviceBayPopulateView.as_view(), name='devicebay_populate'),
    url(r'^device-bays/(?P<pk>\d+)/depopulate/$', views.DeviceBayDepopulateView.as_view(), name='devicebay_depopulate'),
    url(r'^device-bays/rename/$', cached(views.DeviceBayBulkRenameView.as_view()), name='devicebay_bulk_rename'),

    # Inventory items
    url(r'^inventory-items/$', cached(views.InventoryItemListView.as_view()), name='inventoryitem_list'),
    url(r'^inventory-items/import/$', views.InventoryItemBulkImportView.as_view(), name='inventoryitem_import'),
    url(r'^inventory-items/edit/$', views.InventoryItemBulkEditView.as_view(), name='inventoryitem_bulk_edit'),
    url(r'^inventory-items/delete/$', views.InventoryItemBulkDeleteView.as_view(), name='inventoryitem_bulk_delete'),
    url(r'^inventory-items/(?P<pk>\d+)/edit/$', views.InventoryItemEditView.as_view(), name='inventoryitem_edit'),
    url(r'^inventory-items/(?P<pk>\d+)/delete/$', views.InventoryItemDeleteView.as_view(), name='inventoryitem_delete'),
    url(r'^devices/(?P<device>\d+)/inventory-items/add/$', cached(views.InventoryItemEditView.as_view()), name='inventoryitem_add'),

    # Cables
    url(r'^cables/$', cached(views.CableListView.as_view()), name='cable_list'),
    url(r'^cables/import/$', views.CableBulkImportView.as_view(), name='cable_import'),
    url(r'^cables/edit/$', views.CableBulkEditView.as_view(), name='cable_bulk_edit'),
    url(r'^cables/delete/$', views.CableBulkDeleteView.as_view(), name='cable_bulk_delete'),
    url(r'^cables/(?P<pk>\d+)/$', cached(views.CableView.as_view()), name='cable'),
    url(r'^cables/(?P<pk>\d+)/edit/$', views.CableEditView.as_view(), name='cable_edit'),
    url(r'^cables/(?P<pk>\d+)/delete/$', views.CableDeleteView.as_view(), name='cable_delete'),
    url(r'^cables/(?P<pk>\d+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='cable_changelog', kwargs={'model': Cable}),

    # Console/power/interface connections (read-only)
    url(r'^console-connections/$', cached(views.ConsoleConnectionsListView.as_view()), name='console_connections_list'),
    url(r'^power-connections/$', cached(views.PowerConnectionsListView.as_view()), name='power_connections_list'),
    url(r'^interface-connections/$', cached(views.InterfaceConnectionsListView.as_view()), name='interface_connections_list'),

    # Virtual chassis
    url(r'^virtual-chassis/$', cached(views.VirtualChassisListView.as_view()), name='virtualchassis_list'),
    url(r'^virtual-chassis/add/$', cached(views.VirtualChassisCreateView.as_view()), name='virtualchassis_add'),
    url(r'^virtual-chassis/(?P<pk>\d+)/edit/$', views.VirtualChassisEditView.as_view(), name='virtualchassis_edit'),
    url(r'^virtual-chassis/(?P<pk>\d+)/delete/$', views.VirtualChassisDeleteView.as_view(), name='virtualchassis_delete'),
    url(r'^virtual-chassis/(?P<pk>\d+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='virtualchassis_changelog', kwargs={'model': VirtualChassis}),
    url(r'^virtual-chassis/(?P<pk>\d+)/add-member/$', views.VirtualChassisAddMemberView.as_view(), name='virtualchassis_add_member'),
    url(r'^virtual-chassis-members/(?P<pk>\d+)/delete/$', views.VirtualChassisRemoveMemberView.as_view(), name='virtualchassis_remove_member'),

    # Power panels
    url(r'^power-panels/$', cached(views.PowerPanelListView.as_view()), name='powerpanel_list'),
    url(r'^power-panels/add/$', cached(views.PowerPanelCreateView.as_view()), name='powerpanel_add'),
    url(r'^power-panels/import/$', views.PowerPanelBulkImportView.as_view(), name='powerpanel_import'),
    url(r'^power-panels/delete/$', views.PowerPanelBulkDeleteView.as_view(), name='powerpanel_bulk_delete'),
    url(r'^power-panels/(?P<pk>\d+)/$', cached(views.PowerPanelView.as_view()), name='powerpanel'),
    url(r'^power-panels/(?P<pk>\d+)/edit/$', views.PowerPanelEditView.as_view(), name='powerpanel_edit'),
    url(r'^power-panels/(?P<pk>\d+)/delete/$', views.PowerPanelDeleteView.as_view(), name='powerpanel_delete'),
    url(r'^power-panels/(?P<pk>\d+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='powerpanel_changelog', kwargs={'model': PowerPanel}),

    # Power feeds
    url(r'^power-feeds/$', cached(views.PowerFeedListView.as_view()), name='powerfeed_list'),
    url(r'^power-feeds/add/$', cached(views.PowerFeedEditView.as_view()), name='powerfeed_add'),
    url(r'^power-feeds/import/$', views.PowerFeedBulkImportView.as_view(), name='powerfeed_import'),
    url(r'^power-feeds/edit/$', views.PowerFeedBulkEditView.as_view(), name='powerfeed_bulk_edit'),
    url(r'^power-feeds/delete/$', views.PowerFeedBulkDeleteView.as_view(), name='powerfeed_bulk_delete'),
    url(r'^power-feeds/(?P<pk>\d+)/$', cached(views.PowerFeedView.as_view()), name='powerfeed'),
    url(r'^power-feeds/(?P<pk>\d+)/edit/$', views.PowerFeedEditView.as_view(), name='powerfeed_edit'),
    url(r'^power-feeds/(?P<pk>\d+)/delete/$', views.PowerFeedDeleteView.as_view(), name='powerfeed_delete'),
    url(r'^power-feeds/(?P<pk>\d+)/changelog/$', cached(ObjectChangeLogView.as_view()), name='powerfeed_changelog', kwargs={'model': PowerFeed}),

]
