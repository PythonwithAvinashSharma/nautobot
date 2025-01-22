# naas/urls.py
from django.urls import path
from .views import (site_onboarding_view, form_config_view, vlan_config_view, 
                    vlan_config_preview,vlan_config_deploy)

app_name= "naas"


urlpatterns = [
    path("site-onboarding", site_onboarding_view, name="site-onboarding"),
    #path('form-config/', form_config_view, name='form-config'),
    path('vlan-config/', vlan_config_view, name='vlan-config'),
    path('vlan-config-preview/', vlan_config_preview, name='vlan-config-preview'),
    path('vlan-config-deploy/', vlan_config_deploy, name='vlan-config-deploy'),
]