# dashboard_plugin/urls.py

from django.urls import path
from . import views

app_name = "dashboard_plugin"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
]
