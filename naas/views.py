from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.core.serializers import serialize
from nautobot.dcim.models import DeviceType, Rack, Device
from nautobot.dcim.models import Location, LocationType
from nautobot.ipam.models import VLAN, Prefix
from nautobot.extras.models import Tag
from django.urls import reverse
from .forms import SiteOnboardingForm, DeviceForm, VLANConfigurationForm
from django.http import JsonResponse
from nautobot.cloud.models import CloudService
import json
from django.core.exceptions import ObjectDoesNotExist
from uuid import UUID
from django.template import loader


# Define the active status value
ACTIVE_STATUS_NAME = 'Active'  # Replace with the actual value for active status
UNUSED_TAG_NAME = 'unused'  # Replace with the actual value for unused tag

def site_onboarding_view(request):
    if request.method == "POST":
        form = SiteOnboardingForm(request.POST)
        if form.is_valid():
            try:
                router_quantity = int(request.POST.get("router_quantity", "0").strip() or 0)
                switch_quantity = int(request.POST.get("switch_quantity", "0").strip() or 0)
                prefix_quantity = int(request.POST.get("prefix_quantity", "0").strip() or 0)
                site_onboarding = form.save()
            except ValueError as e:
                return JsonResponse({"error": f"Invalid input: {e}"}, status=400)

            # Handle router devices
            for i in range(router_quantity):
                device_form = DeviceForm({
                    'name': request.POST.get(f'router_name_{i}', '').strip(),
                    'device_type': request.POST.get(f'router_device_type_{i}', None),
                    'rack': request.POST.get(f'router_rack_{i}', None),
                    'tags': request.POST.getlist(f'router_tags_{i}', []),
                    'serial_number': request.POST.get(f'router_serial_number_{i}', '').strip(),
                    'management_ip_address': request.POST.get(f'router_mgmt_ip_{i}', '').strip(),
                })
                if device_form.is_valid():
                    device = device_form.save(commit=False)
                    device.site_onboarding = site_onboarding
                    device.save()
                    device.tags.set(device_form.cleaned_data['tags'])

            # Handle switch devices
            for i in range(switch_quantity):
                device_form = DeviceForm({
                    'name': request.POST.get(f'switch_name_{i}'),
                    'device_type': request.POST.get(f'switch_device_type_{i}'),
                    'rack': request.POST.get(f'switch_rack_{i}'),
                    'tags': request.POST.getlist(f'switch_tags_{i}'),
                    'serial_number': request.POST.get(f'switch_serial_number_{i}'),
                    'management_ip_address': request.POST.get(f'switch_mgmt_ip_{i}')
                })
                if device_form.is_valid():
                    device = device_form.save(commit=False)
                    device.site_onboarding = site_onboarding
                    device.save()
                    device.tags.set(device_form.cleaned_data['tags'])

            return redirect('naas:site_onboarding')  # Replace 'success_url' with your success URL
    else:
        form = SiteOnboardingForm()

    device_types_json = serialize('json', DeviceType.objects.all())
    racks_json = serialize('json', Rack.objects.filter(status__name=ACTIVE_STATUS_NAME, tags__name=UNUSED_TAG_NAME))
    prefixes_json = serialize('json', Prefix.objects.filter(status__name=ACTIVE_STATUS_NAME, tags__name=UNUSED_TAG_NAME))
    vlans_json = serialize('json', VLAN.objects.filter(status__name=ACTIVE_STATUS_NAME, tags__name=UNUSED_TAG_NAME))

    # Get tags for devices
    device_tags = Tag.objects.get_for_model(Device)
    device_tags_json = serialize('json', device_tags)

    # Get tags for prefixes
    prefix_tags = Tag.objects.get_for_model(Prefix)
    prefix_tags_json = serialize('json', prefix_tags)

    # Get tags for cloud services
    cloud_service_tags = Tag.objects.get_for_model(CloudService)
    cloud_service_tags_json = serialize('json', cloud_service_tags)

    return render(request, 'naas/naas.html', {
        'form': form,
        'device_types_json': device_types_json,
        'racks_json': racks_json,
        'tags_json': device_tags_json,
        'prefixes_json': prefixes_json,
        'vlans_json': vlans_json,
        'prefix_tags_json': prefix_tags_json,
        'cloud_service_tags_json': cloud_service_tags_json,
    })

def is_valid_uuid(value):
    try:
        UUID(str(value))
        return True
    except ValueError:
        return False

def form_config_view(request):
    if request.method == 'POST':
        form_data = json.loads(request.body)
        return JsonResponse(form_data)
    else:
        form_data = json.loads(request.GET.get('data', '{}'))
        
        # Fetch actual values from the database
        for key, value in form_data.items():
            if key == 'csrfmiddlewaretoken':
                continue  # Skip the CSRF token
            if is_valid_uuid(value):
                try:
                    if key == 'location':
                        form_data[key] = Location.objects.get(pk=value).name
                    elif key.startswith('device_type_'):
                        form_data[key] = DeviceType.objects.get(pk=value).model
                    elif key.startswith('rack_'):
                        form_data[key] = Rack.objects.get(pk=value).name
                    elif key.startswith('tags_') or key == 'site_tags':
                        form_data[key] = Tag.objects.get(pk=value).name
                    elif key.startswith('prefix_'):
                        form_data[key] = Prefix.objects.get(pk=value).prefix
                    elif key.startswith('vlan_'):
                        form_data[key] = VLAN.objects.get(pk=value).name
                    elif key.startswith('prefix_tags_'):
                        form_data[key] = Tag.objects.get(pk=value).name
                except ObjectDoesNotExist:
                    form_data[key] = 'Not Found'
            else:
                # Handle non-UUID values if necessary
                form_data[key] = value

def vlan_config_view(request):
    if request.method == 'POST':
        form = VLANConfigurationForm(request.POST)
        print("here")  # Debugging statement
        if form.is_valid():
            form_data = form.cleaned_data
            form_data['vlan'] = str(form_data['vlan'])  # Convert VLAN object to string
            print("Form Data:", form_data)  # Debugging statement
            return render(request, 'naas/vlan_config_preview.jinja2', {'form_data': json.dumps(form_data)})
    else:
        form = VLANConfigurationForm()
        print("there")  # Debugging statement
    return render(request, 'naas/vlan_config.html', {'form': form})

def vlan_config_preview(request):
    if request.method == 'POST':
        form = VLANConfigurationForm(request.POST)
        if form.is_valid():
            # Prepare data for preview
            form_data = {
                'switch_ip': form.cleaned_data['switch_ip'],
                'vlan': str(form.cleaned_data['vlan']),
                'admin_state': form.cleaned_data['admin_state'],
                'vlan_description': form.cleaned_data.get('vlan_description', '')
            }
            
            # Create context for the template
            context = {
                'form_data': form_data,
                'csrf_token': request.POST.get('csrfmiddlewaretoken', ''),
            }
            
            # Render the template
            template = loader.get_template('naas/vlan_config_preview.jinja2')
            return render(request, 'naas/vlan_config_preview.jinja2', context)
        else:
            # If form is invalid, return to form with errors
            return render(request, 'naas/vlan_config.html', {'form': form})
    
    return HttpResponseRedirect(reverse('plugins:naas:vlan-config'))

def vlan_config_deploy(request):
    if request.method == 'POST':
        try:
            form_data = json.loads(request.POST.get('form_data', '{}'))
            # Implement your deployment logic here
            return JsonResponse({
                'status': 'success', 
                'message': 'VLAN configuration deployed successfully'
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error', 
                'message': 'Invalid form data'
            }, status=400)
    return JsonResponse({
        'status': 'error', 
        'message': 'Invalid request method'
    }, status=400)