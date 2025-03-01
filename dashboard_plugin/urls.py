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

    path("kpi_metrics/", views.KpiMetrics, name='kpi_metrics'),
    path("ai_ops/", views.AIOpsScore, name='ai_ops'),
    path("application_experience/", views.ApplicationExperience, name='application_experience'),
    path("capacity_planning/", views.CapacityPlanning, name='capacity_planning'),
    path("routing_observability/", views.RoutingObservability, name='routing_observability'),
    path("sustainability_score/", views.SustainabilityScore, name='sustainability_score'),
    path("vulnerability_score/", views.VunlnerabilityScore, name='vulnerability_score'),
    path("top_talkers/", views.TopTalkers, name='top_talkers'),
    

]
