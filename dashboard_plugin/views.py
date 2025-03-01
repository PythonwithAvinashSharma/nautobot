# dashboard_plugin/views.py

from django.shortcuts import render

def dashboard_view(request):
    return render(request, "dashboard_plugin/dashboard.html")

def AddDashboardView(request):
    return render(request, "dashboard_plugin/add_dashboard.html")

def device_inventory(request):
    return render(request, 'dashboard_plugin/device_inventory.html')

def site_dashboard(request):
    return render(request, 'dashboard_plugin/site_dashboard.html')

def racks(request):
    return render(request, 'dashboard_plugin/racks.html')

def ip_addresses(request):
    return render(request, 'dashboard_plugin/ip_addresses.html')

def prefixes(request):
    return render(request, 'dashboard_plugin/prefixes.html')

def vlans(request):
    return render(request, 'dashboard_plugin/vlans.html')

def circuits(request):
    return render(request, 'dashboard_plugin/circuits.html')

def lcm_network(request):
    return render(request, 'dashboard_plugin/lcm_network.html')

def amsterdam_site(request):
    return render(request, 'dashboard_plugin/amsterdam_site.html')

def KpiMetrics(request):
    return render(request, 'dashboard_plugin/kpi_metrics.html')

def AIOpsScore(request):
    return render(request, 'dashboard_plugin/ai_ops_score.html')

def ApplicationExperience(request):
    return render(request, 'dashboard_plugin/application_experience.html')

def CapacityPlanning(request):
    return render(request, 'dashboard_plugin/capacity_planning.html')

def RoutingObservability(request):
    return render(request, 'dashboard_plugin/routing_observablity.html')

def SustainabilityScore(request):
    return render(request, 'dashboard_plugin/sustainability_score.html')

def VunlnerabilityScore(request):
    return render(request, 'dashboard_plugin/vulnerability_score.html')

def TopTalkers(request):
    return render(request, 'dashboard_plugin/top_talkers.html')