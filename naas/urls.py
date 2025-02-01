# naas/urls.py
from django.urls import path
from .views import (site_onboarding_view, 
                    form_config_view, 
                    vlan_config_view, 
                    vlan_config_preview,
                    vlan_config_deploy, 
                    get_subnets, 
                    fetch_change_request,
                    log_validator_details,
                    switches_view,
                    cisco_detailed_view,
                    arista_detailed_view,
                    hpe_detailed_view,
                    juniper_detailed_view,
                    aci_templates_list,
                    aci_vlan_to_port_form,
                    aci_vlan_to_port_submit,
                    aci_vlan_to_port_preview,
                    get_device_status_view)

app_name= "naas"


urlpatterns = [
    path("site-onboarding", site_onboarding_view, name="site-onboarding"),
    #path('form-config/', form_config_view, name='form-config'),
    path('vlan-config/', vlan_config_view, name='vlan-config'),
    path('vlan-config-preview/', vlan_config_preview, name='vlan-config-preview'),
    path('vlan-config-deploy/', vlan_config_deploy, name='vlan-config-deploy'),
    path('get-subnets/<str:vlan_id>/', get_subnets, name='get-subnets'),
    path('fetch-change-request/<str:cr_number>/', fetch_change_request, name='fetch-change-request'),
    path('log-validator-details/', log_validator_details, name='log_validator_details'),
    path('switches/', switches_view, name='switches'),
    path('switches/cisco_detailed/', cisco_detailed_view, name='cisco_detailed'),
    path('switches/arista_detailed/', arista_detailed_view, name='arista_detailed'),
    path('switches/hpe_detailed/', hpe_detailed_view, name='hpe_detailed'),
    path('switches/juniper_detailed/', juniper_detailed_view, name='juniper_detailed'),
    path('aci-templates/', aci_templates_list, name='aci_templates_list'),
    path('aci-vlan-to-port/', aci_vlan_to_port_form, name='aci_vlan_to_port_form'),
    path('aci-vlan-to-port/preview/', aci_vlan_to_port_preview, name='aci_vlan_to_port_preview'),
    path('aci-vlan-to-port/submit/', aci_vlan_to_port_submit, name='aci_vlan_to_port_submit'),
    path('get-device-status/', get_device_status_view, name='get-device-status'),
]