from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.core.serializers import serialize
from nautobot.dcim.models import DeviceType, Rack, Device
from nautobot.dcim.models import Location, LocationType
from nautobot.ipam.models import VLAN, Prefix
from nautobot.extras.models import Tag
from django.urls import reverse
from .forms import SiteOnboardingForm, DeviceForm, MultiVLANConfigurationForm, ACIConfigForm
from django.http import JsonResponse
from nautobot.cloud.models import CloudService
import json
from django.core.exceptions import ObjectDoesNotExist
from uuid import UUID
from django.template import loader
from netmiko import ConnectHandler
import requests
from requests.auth import HTTPBasicAuth
import re
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_GET, require_POST
import logging

logger = logging.getLogger(__name__)


# Define the active status value
ACTIVE_STATUS_NAME = 'Active'  # Replace with the actual value for active status
UNUSED_TAG_NAME = 'unused'  # Replace with the actual value for unused tag

logger = logging.getLogger(__name__)

def get_device_connection(ip, username, password):
    device = {
        'device_type': 'arista_eos',
        'host': ip,
        'username': username,
        'password': password,
    }
    return ConnectHandler(**device)
def configure_arista_vlan(ip, username, password, vlan_id, vlan_name, gateway_ip, subnet, mtu_size):
    try:
        logger.info(f"Connecting to {ip} with username {username}")
        with get_device_connection(ip, username, password) as net_connect:
            logger.info(f"Connected to {ip}")

            # Enter enable and config modes
            net_connect.enable()
            net_connect.config_mode()

            # Sanitize VLAN name (replace spaces with underscores)
            sanitized_vlan_name = vlan_name.replace(' ', '_')

            # Prepare IP address with subnet prefix
            ip_with_subnet = f"{gateway_ip}/{subnet.split('/')[-1]}"

            # Prepare configuration commands
            commands = [
                f'vlan {vlan_id}',  # Define VLAN ID
                f'name {sanitized_vlan_name}',  # Set VLAN name
                f'interface vlan {vlan_id}',  # Configure VLAN interface
                f'ip address {ip_with_subnet}',  # Assign IP address with subnet
                f'mtu {mtu_size}',  # Set MTU size
                'no shutdown',  # Enable interface
            ]

            logger.info(f"Sending configuration commands to {ip}: {commands}")
            # Execute commands
            output = net_connect.send_config_set(commands)

            # Save configuration
            net_connect.save_config()

            logger.info(f"Configuration successful for {ip}")
            return output

    except Exception as e:
        logger.error(f"Error configuring VLAN on {ip}: {e}")
        return str(e)

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

@login_required
def vlan_config_view(request):
    form = MultiVLANConfigurationForm()
    return render(request, 'naas/vlan_config.html', {'form': form})


def vlan_config_preview(request):
    if request.method == 'POST':
        form = MultiVLANConfigurationForm(data=request.POST)
        if form.is_valid():
            configs = []
            for row_data in form.cleaned_data():
                vlan = VLAN.objects.get(id=row_data['vlan'].id)

                # Extract and calculate the ip_with_subnet value
                gateway_ip = row_data.get('gateway_ip', '')
                subnet = str(row_data.get('subnet', ''))
                ip_with_subnet = f"{gateway_ip}/{subnet.rsplit('/')[-1]}" if gateway_ip and subnet else ''

                config = {
                    'switch_ip': row_data['switch_ip'],
                    'vlan': vlan.vid,  # Use the VLAN's numeric ID
                    'admin_state': row_data['admin_state'],
                    'vlan_description': row_data.get('vlan_description', ''),
                    'subnet': str(row_data.get('subnet', '')),
                    'gateway_ip': row_data.get('gateway_ip', ''),
                    'ip_with_subnet': ip_with_subnet,
                    'mtu_size': row_data.get('mtu_size', '')
                }
                configs.append(config)
            
            if configs:
                return render(request, 'naas/vlan_config_preview.jinja2', {
                    'configs': configs,
                    'configs_json': json.dumps(configs)
                })
        
        # If form is invalid or no configs, return to form with errors
        return render(request, 'naas/vlan_config.html', {'form': form})
    
    return HttpResponseRedirect(reverse('plugins:naas:vlan-config'))

def get_subnets(request, vlan_id):
    try:
        vlan_uuid = UUID(vlan_id)
        subnets = Prefix.objects.filter(vlan_id=vlan_uuid)
        subnets_data = [{'id': str(subnet.id), 'prefix': str(subnet)} for subnet in subnets]
        return JsonResponse({'subnets': subnets_data})
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid VLAN ID'}, status=400)


@csrf_protect    
def vlan_config_deploy(request):
    if request.method == 'POST':
        try:
            configs = json.loads(request.POST.get('configs', '[]'))
            username = 'hcl'
            password = 'cisco'

            results = []
            for config in configs:
                result = configure_arista_vlan(
                    ip=config['switch_ip'],
                    username=username,
                    password=password,
                    vlan_id=config['vlan'],
                    vlan_name=config['vlan_description'],
                    gateway_ip=config['gateway_ip'],
                    subnet=config['subnet'],
                    mtu_size=config['mtu_size']
                )
                results.append(result)

            # Preprocess results to split lines for the template
            formatted_results = [result.split("\n") for result in results]
            context = {
                "status": 'success',
                "message": 'VLAN configuration deployed successfully',
                "output": formatted_results  # Now each result is a list of lines
            }
            return render(request, "naas/vlan_config_response.html", context)

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid form data'
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

def get_servicenow_change_request(cr_number):
    url = f'https://hclpocm1.service-now.com/api/now/table/change_request?sysparm_query=number={cr_number}'
    auth = HTTPBasicAuth('advisory_bot@hcltech.com', 'Sept@2024')
    headers = {
        'Accept': 'application/json'
    }
    response = requests.get(url, auth=auth, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def parse_description(short_description, description):
    parsed_data = {}
    combined_text = f"{short_description}\n{description}"
    if 'ARISTA' in combined_text:
        switch_ip_match = re.search(r'Switch IP:\s*([\d\.]+)', description)
        vlan_match = re.search(r'vlan\s*(\d+)', description, re.IGNORECASE)
        subnet_match = re.search(r'Subnet\s*:\s*([\d\.\/]+)', description)
        gateway_ip_match = re.search(r'GW:\s*([\d\.\/]+)', description)
        description_match = re.search(r'description:\s*(.*)', description, re.IGNORECASE)
        mtu_match = re.search(r'mtu\s*:\s*(\d+)', description, re.IGNORECASE)
        if switch_ip_match:
            parsed_data['switch_ip'] = switch_ip_match.group(1)
        if vlan_match:
            parsed_data['vlan'] = vlan_match.group(1)
        if subnet_match:
            parsed_data['subnet'] = subnet_match.group(1)
        if gateway_ip_match:
            parsed_data['gateway_ip'] = gateway_ip_match.group(1)
        if description_match:
            parsed_data['description'] = description_match.group(1).strip()
        if mtu_match:
            parsed_data['mtu'] = mtu_match.group(1)
    elif 'CISCO' in combined_text and 'ACI' in combined_text:
        fabric_name_match = re.search(r'fabricName:\s*(\S+)', description)
        pod_id_match = re.search(r'podId:\s*(\d+)', description)
        node_id_match = re.search(r'nodeId:\s*(\d+)', description)
        tenant_match = re.search(r'Tenant:\s*(\S+)', description)
        ap_match = re.search(r'AP:\s*(\S+)', description)
        epg_match = re.search(r'EPG:\s*(\S+)', description)
        vlan_match = re.search(r'vlan:\s*(\d+)', description)
        mode_match = re.search(r'mode:\s*(\S+)', description)
        from_port_match = re.search(r'fromPort:\s*(\d+)', description)
        to_port_match = re.search(r'toPort:\s*(\d+)', description)
        if fabric_name_match:
            parsed_data['fabric_name'] = fabric_name_match.group(1)
        if pod_id_match:
            parsed_data['pod_id'] = pod_id_match.group(1)
        if node_id_match:
            parsed_data['node_id'] = node_id_match.group(1)
        if tenant_match:
            parsed_data['tenant'] = tenant_match.group(1)
        if ap_match:
            parsed_data['ap'] = ap_match.group(1)
        if epg_match:
            parsed_data['epg'] = epg_match.group(1)
        if vlan_match:
            parsed_data['vlan'] = vlan_match.group(1)
        if mode_match:
            parsed_data['mode'] = mode_match.group(1)
        if from_port_match:
            parsed_data['from_port'] = from_port_match.group(1)
        if to_port_match:
            parsed_data['to_port'] = to_port_match.group(1)
    return parsed_data

@require_GET
def fetch_change_request(request, cr_number):
    cr_data = get_servicenow_change_request(cr_number)
    description = cr_data['result'][0]['description']
    short_description = cr_data['result'][0]['short_description']

    parsed_data = parse_description(short_description, description)

    if cr_data:
        return JsonResponse({
            'status': 'success',
            'description': 'Title: ' + short_description + '\nDescription: ' + description,
            'parsed_data': parsed_data
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Change request not found'
        }, status=404)


@csrf_exempt
@require_POST
def log_validator_details(request):
    import json
    data = json.loads(request.body)
    name = data.get('name')
    email = data.get('email')
    employee_id = data.get('employee_id')

    if name and email and employee_id:
        logger.info(f'Validator Name: {name}')
        logger.info(f'Validator Email: {email}')
        logger.info(f'Validator Employee ID: {employee_id}')
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

@csrf_exempt
@require_POST
def run_command(request):
    data = json.loads(request.body)
    command = data.get('command')
    ip = data.get('ip')
    username = data.get('username')
    password = data.get('password')

    if not command:
        return JsonResponse({'status': 'error', 'message': 'No command provided'}, status=400)

    try:
        with get_device_connection(ip, username, password) as net_connect:
            output = net_connect.send_command(command)
        return JsonResponse({'status': 'success', 'output': output})
    except Exception as e:
        logger.error(f'Failed to run command: {e}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def switches_view(request):
    return render(request, 'naas/switches.html')

def cisco_detailed_view(request):
    return render(request, 'naas/cisco_detailed.html')

def arista_detailed_view(request):
    return render(request, 'naas/arista_detailed.html')

def hpe_detailed_view(request):
    return render(request, 'naas/hpe_detailed.html')

def juniper_detailed_view(request):
    return render(request, 'naas/juniper_detailed.html')


@csrf_exempt
def aci_config(request):
    if request.method == 'POST':
        form = ACIConfigForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Define APIC IP and credentials
            apic_ip = "sandboxapicdc.cisco.com"
            usr = "admin"
            pwd = "!v3G@!4@Y"

            # Define URL and credentials for RESTAPI authentication
            auth_url = "https://%s/api/aaaLogin.json" % apic_ip
            headers = {'content-type': 'application/json'}
            payload = {
                "aaaUser": {
                    "attributes": {
                        "name": usr,
                        "pwd": pwd
                    }
                }
            }

            # Suppress warnings when restapi uses https with self-signed certificate
            requests.packages.urllib3.disable_warnings()

            # Authenticate in APIC and save the security token
            response = requests.post(auth_url, data=json.dumps(payload), headers=headers, verify=False, timeout=10)
            if response.status_code == 200:
                apic_auth_cookie = response.cookies
            else:
                return render(request, 'aci_config.html', {'form': form, 'error': 'Authentication failed'})

            # Read the jinja2 template
            mytemplatefile = 'config_template.j2'
            myjloader = jinja2.FileSystemLoader(os.getcwd())
            myjenv = jinja2.Environment(loader=myjloader, trim_blocks=True, lstrip_blocks=True)
            myjtemplate = myjenv.get_template(mytemplatefile)

            # Prepare data for jinja2 template
            dictforjinja = {
                'fabricName': data['fabricName'],
                'podId': data['podId'],
                'nodeId': data['nodeId'],
                'Tenant': data['Tenant'],
                'AP': data['AP'],
                'EPG': data['EPG'],
                'vlan': data['vlan'],
                'mode': 'regular' if data['mode'] == 'trunk' else 'untagged',
                'fromPort': data['fromPort'],
                'toPort': data['toPort']
            }

            # Generate the XML payload
            myresult = myjtemplate.render(var=dictforjinja)

            # Define POST url for RESTAPI, target the correct EPG object
            post_url = "https://%s/api/mo/uni/tn-%s/ap-%s/epg-%s.xml" % (apic_ip, dictforjinja['Tenant'], dictforjinja['AP'], dictforjinja['EPG'])

            # POST the XML result created from template and data from the form
            headers = {'content-type': 'application/xml'}
            response = requests.post(post_url, data=myresult, cookies=apic_auth_cookie, headers=headers, verify=False, timeout=5)

            if response.status_code == 200:
                return render(request, 'naas/aci_config.html', {'form': form, 'success': 'Configuration applied successfully'})
            else:
                return render(request, 'naas/aci_config.html', {'form': form, 'error': 'Configuration failed'})

    else:
        form = ACIConfigForm()

    return render(request, 'naas/aci_config.html', {'form': form})

def aci_templates_list(request):
    return render(request, 'naas/aci_list_templates.html')

# def aci_vlan_to_port_form(request):
#     if request.method == 'POST':
#         form = ACIConfigForm(request.POST)
#         if form.is_valid():
#             config_data = form.cleaned_data
#             config_preview = loader.render_to_string('naas/aci_vlan_to_port.jinja2', {'var': config_data})
#             return render(request, 'naas/aci_vlan_to_port_preview.html', {'config_preview': config_preview, 'config_data': config_data})
#     else:
#         form = ACIConfigForm()
#     return render(request, 'naas/aci_vlan_to_port_form.html', {'form': form})

def aci_vlan_to_port_preview(request):
    if request.method == 'POST':
        try:
            # Print the POST data for debugging
            print("POST data:", request.POST)
            
            # Convert to integers
            from_port = int(request.POST['fromPort'])
            to_port = int(request.POST['toPort'])
            
            # Create config_data
            config_data = {
                'tenant': request.POST['tenant'],
                'ap': request.POST['ap'],
                'epg': request.POST['epg'],
                'fromPort': from_port,
                'toPort': to_port,
                'vlan': request.POST['vlan'],
                'mode': request.POST['mode'],
                'podId': request.POST['podId'],
                'nodeId': request.POST['nodeId']
            }
            
            # Print config_data for debugging
            print("Config data:", config_data)

            # Create the port range
            port_list = list(range(from_port, to_port + 1))
            
            # Create template context
            template_context = {
                'var': {
                    **config_data,
                    'port_range': port_list
                }
            }
            
            # Print template context for debugging
            print("Template context:", template_context)

            # Render the configuration
            config_preview = loader.render_to_string(
                'naas/aci_vlan_to_port.jinja2', 
                template_context
            )

            print("Final config_preview being sent to template:\n", config_preview)
            
            return render(
            request, 
            'naas/aci_vlan_to_port_preview.html', 
            {
                'config_preview': config_preview,  # Pass the raw Jinja output
                'config_data': config_data
            }
        )
        except ValueError as e:
            print("Error:", str(e))  # Debug print
            return HttpResponse(f"Error: {str(e)}")
        except Exception as e:
            print("Unexpected error:", str(e))  # Debug print
            return HttpResponse(f"Unexpected error: {str(e)}")

    return redirect('aci_vlan_to_port_form')

def aci_vlan_to_port_submit(request):
    if request.method == 'POST':
        config_data = request.POST
        # Process the form data and integrate with ServiceNow or other services
        # ...
        return HttpResponse("Configuration deployed successfully.")
    return redirect('aci_vlan_to_port_form')