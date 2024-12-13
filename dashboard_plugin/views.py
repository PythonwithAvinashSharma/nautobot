# dashboard_plugin/views.py

from django.shortcuts import render

def dashboard_view(request):
    return render(request, "dashboard_plugin/dashboard.html")
