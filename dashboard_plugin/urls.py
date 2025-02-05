# dashboard_plugin/urls.py

from django.urls import path
from . import views

app_name = "dashboard_plugin"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("", views.AddDashboardView, name="add_dashboard"),
    path("device_inventory/", views.device_inventory, name='device_inventory'),
    path("site_dashboard/", views.site_dashboard, name='site_dashboard'),
    
    path("racks/", views.racks, name='racks'),
    path("ip_addresses/", views.ip_addresses, name='ip_addresses'),
    path("prefixes/", views.prefixes, name='prefixes'),
    path("vlans/", views.vlans, name='vlans'),
    path("circuits/", views.circuits, name='circuits'),

    path("lcm_network/", views.lcm_network, name='lcm_network'),
    path("amsterdam_site/", views.amsterdam_site, name='amsterdam_site'),

]
