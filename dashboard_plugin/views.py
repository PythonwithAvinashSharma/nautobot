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