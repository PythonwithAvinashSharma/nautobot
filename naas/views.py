from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.core.serializers import serialize
from nautobot.dcim.models import DeviceType, Rack, Device
from nautobot.dcim.models import Location, LocationType
from nautobot.ipam.models import VLAN, Prefix
from nautobot.extras.models import Tag
from django.urls import reverse
import urllib3
from .forms import SiteOnboardingForm, DeviceForm, MultiVLANConfigurationForm, ACIConfigForm
from django.http import JsonResponse
from nautobot.cloud.models import CloudService
import json
from django.core.exceptions import ObjectDoesNotExist
from uuid import UUID
import jinja2
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
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


# Define the active status value
ACTIVE_STATUS_NAME = 'Active'  
UNUSED_TAG_NAME = 'unused'
APIC_IP = "sandboxapicdc.cisco.com"
TEMPLATE_FILE = 'config_template.j2'
RESULT_FILE = 'aci_results.xml'
USR = "admin"
PWD = "!v3G@!4@Y"


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

                sanitized_switch_ip = row_data['switch_ip'].replace('.', '_')

                config = {
                    'switch_ip': row_data['switch_ip'],
                    'vlan': vlan.vid,  # Use the VLAN's numeric ID
                    'admin_state': row_data['admin_state'],
                    'vlan_description': row_data.get('vlan_description', ''),
                    'subnet': str(row_data.get('subnet', '')),
                    'gateway_ip': row_data.get('gateway_ip', ''),
                    'ip_with_subnet': ip_with_subnet,
                    'mtu_size': row_data.get('mtu_size', ''),
                    'sanitized_switch_ip' :sanitized_switch_ip
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
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

def aci_vlan_to_port_form(request):
    if request.method == 'POST':
        form = ACIConfigForm(request.POST)
        if form.is_valid():
            config_data = form.cleaned_data
            config_preview = loader.render_to_string('naas/aci_vlan_to_port.jinja2', {'var': config_data})
            return render(request, 'naas/aci_vlan_to_port_preview.html', {'config_preview': config_preview, 'config_data': config_data})
    else:
        form = ACIConfigForm()
    return render(request, 'naas/aci_vlan_to_port_form.html', {'form': form})

def aci_vlan_to_port_preview(request):
    if request.method == 'POST':
        try:
            print("POST data:", request.POST)
            
            from_port = int(request.POST['fromPort'])
            to_port = int(request.POST['toPort'])
            
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
            
            print("Config data:", config_data)
            
            template_context = {
                'var': {
                    **config_data,
                    'port_range': list(range(from_port, to_port + 1))
                }
            }
            
            print("Template context:", template_context)
            
            # Get the absolute path to the template
            template_path = 'naas/aci_vlan_to_port.jinja2'
            print(f"Looking for template at: {template_path}")
            
            try:
                config_preview = loader.render_to_string(
                    template_path,
                    template_context
                )
                print("Rendered config_preview:", config_preview)
                print("Length of config_preview:", len(config_preview))
            except Exception as template_error:
                print("Template rendering error:", str(template_error))
                return HttpResponse(f"Template error: {str(template_error)}")
            
            config_preview = loader.render_to_string(
                template_path,
                template_context
            )
            
            # Try to force string conversion and strip any problematic characters
            config_preview = str(config_preview).strip()
            
            # Add some test content to verify rendering
            #config_preview = "START\n" + config_preview + "\nEND"
            
            context = {
                'config_preview': config_preview,
                'config_data': config_data
            }
            
            return render(request, 'naas/aci_vlan_to_port_preview.html', context)
            
        except Exception as e:
            print(f"Error in view: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return HttpResponse(f"Error: {str(e)}")
    
    return redirect('aci_vlan_to_port_form')

def aci_vlan_to_port_submit(request):
    if request.method == 'POST':
        try:
            config_preview = request.POST.get('config_preview')
            config_data_str = request.POST.get('config_data')
            print("Config data (raw):", config_data_str)
            print("Config preview (XML):", config_preview)

            # Parse the JSON string
            try:
                if config_data_str.startswith("{") and config_data_str.endswith("}"):
                    config_data_str = config_data_str.replace("'", "\"")
                config_data = json.loads(config_data_str)
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                return render(request, 'naas/aci_config_response.html', {
                    'status_class': 'error',
                    'message': f"Invalid JSON data: {str(e)}"
                })

            # Define the APIC IP and credentials
            apic_ip = "sandboxapicdc.cisco.com"
            usr = "admin"
            pwd = "!v3G@!4@Y"

            # Define URL and credentials for RESTAPI authentication
            auth_url = f"https://{apic_ip}/api/aaaLogin.json"
            headers = {'content-type': 'application/json'}
            auth_payload = {
                "aaaUser": {
                    "attributes": {
                        "name": usr,
                        "pwd": pwd
                    }
                }
            }

            # Suppress warnings for self-signed certificates
            requests.packages.urllib3.disable_warnings()

            # Authenticate with APIC
            auth_response = requests.post(auth_url, data=json.dumps(auth_payload), headers=headers, verify=False, timeout=10)
            print("\n--- AUTH response is %s" % auth_response)
            
            if auth_response.status_code != 200:
                return render(request, 'naas/aci_config_response.html', {
                    'status_class': 'error',
                    'message': "Authentication failed."
                })

            cookies = auth_response.cookies
            headers = {'content-type': 'application/xml'}

            # 1. Create Tenant if it doesn't exist
            tenant_xml = f"""
            <fvTenant name="{config_data['tenant']}">
            </fvTenant>
            """
            tenant_url = f"https://{apic_ip}/api/mo/uni/tn-{config_data['tenant']}.xml"
            tenant_response = requests.post(tenant_url, data=tenant_xml, cookies=cookies, headers=headers, verify=False, timeout=5)
            print("Tenant creation response:", tenant_response.status_code)
            
            if tenant_response.status_code != 200:
                return render(request, 'naas/aci_config_response.html', {
                    'status_class': 'error',
                    'message': f"Failed to create tenant. Error: {tenant_response.content.decode('utf-8')}"
                })

            # 2. Create Application Profile if it doesn't exist
            ap_xml = f"""
            <fvAp name="{config_data['ap']}">
            </fvAp>
            """
            ap_url = f"https://{apic_ip}/api/mo/uni/tn-{config_data['tenant']}/ap-{config_data['ap']}.xml"
            ap_response = requests.post(ap_url, data=ap_xml, cookies=cookies, headers=headers, verify=False, timeout=5)
            print("AP creation response:", ap_response.status_code)
            
            if ap_response.status_code != 200:
                return render(request, 'naas/aci_config_response.html', {
                    'status_class': 'error',
                    'message': f"Failed to create Application Profile. Error: {ap_response.content.decode('utf-8')}"
                })

            # 3. Create EPG if it doesn't exist
            epg_xml = f"""
            <fvAEPg name="{config_data['epg']}">
                <fvRsDomAtt tDn="uni/phys-phys"/>
            </fvAEPg>
            """
            epg_url = f"https://{apic_ip}/api/mo/uni/tn-{config_data['tenant']}/ap-{config_data['ap']}/epg-{config_data['epg']}.xml"
            epg_response = requests.post(epg_url, data=epg_xml, cookies=cookies, headers=headers, verify=False, timeout=5)
            print("EPG creation response:", epg_response.status_code)
            
            if epg_response.status_code != 200:
                return render(request, 'naas/aci_config_response.html', {
                    'status_class': 'error',
                    'message': f"Failed to create EPG. Error: {epg_response.content.decode('utf-8')}"
                })

            # 4. Now deploy the port bindings
            # Translate mode values in config_preview
            if config_data['mode'] == 'access':
                config_preview = config_preview.replace('mode="access"', 'mode="untagged"')
            elif config_data['mode'] == 'trunk':
                config_preview = config_preview.replace('mode="trunk"', 'mode="regular"')

            # POST the port binding configuration
            post_url = f"https://{apic_ip}/api/mo/uni/tn-{config_data['tenant']}/ap-{config_data['ap']}/epg-{config_data['epg']}.xml"
            print("POST URL:", post_url)
            
            response = requests.post(
                post_url, 
                data=config_preview, 
                cookies=cookies, 
                headers=headers, 
                verify=False, 
                timeout=5
            )

            print("POST response status code:", response.status_code)
            print("POST response content:", response.content.decode('utf-8'))

            # Check for successful configuration
            if response.status_code == 200 and '<imdata totalCount="0">' in response.content.decode('utf-8'):
                return render(request, 'naas/aci_config_response.html', {
                    'status_class': 'success',
                    'message': "Configuration deployed successfully!",
                    'output': response.content.decode('utf-8')
                })
            else:
                return render(request, 'naas/aci_config_response.html', {
                    'status_class': 'error',
                    'message': f"Failed to deploy configuration. Error: {response.content.decode('utf-8')}"
                })

        except Exception as e:
            print(f"Error in view: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return render(request, 'naas/aci_config_response.html', {
                'status_class': 'error',
                'message': f"Error: {str(e)}"
            })

    return redirect('aci_vlan_to_port_form')

def get_show_vlan(net_connect, vlan_id=None):
    """Get show vlan output from device"""
    command = f'show vlan {vlan_id}' if vlan_id else 'show vlan brief'
    return net_connect.send_command(command)

def get_show_ip_interface_brief(net_connect, vlan_id=None):
    """Get show ip interface brief output from device"""
    command = f'show ip interface vlan {vlan_id}' if vlan_id else 'show ip interface brief'
    return net_connect.send_command(command)

@csrf_exempt
def get_device_status_view(request):
    """View to handle device status retrieval request"""
    if request.method == 'POST':
        try:
            # Parse incoming JSON data
            data = json.loads(request.body)
            switch_ip = data.get('switch_ip')
            command = data.get('command')
            vlan_id = data.get('vlan_id', None)
            
            # Use hardcoded or environment-based credentials
            username = data.get('username', 'hcl')  # Consider using environment variables
            password = data.get('password', 'cisco')
            
            # Retrieve device status
            result = get_device_status(switch_ip, username, password, command, vlan_id)
            
            # Return appropriate response based on command
            if result['status'] == 'success':
                if command.startswith('show vlan'):
                    return JsonResponse({
                        'status': 'success',
                        'vlan_output': result['output']
                    })
                elif command.startswith('show ip interface vlan') or command == 'show ip interface brief':
                    return JsonResponse({
                        'status': 'success',
                        'ip_interface_output': result['output']
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid command'
                    }, status=400)
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': result.get('error', 'Unknown error')
                }, status=500)
        
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON'
            }, status=400)
        
        except Exception as e:
            logger.error(f"Unexpected error in get_device_status_view: {e}")
            return JsonResponse({
                'status': 'error',
                'message': 'Internal server error'
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)


def get_device_status(ip, username, password, command, vlan_id=None):
    """Get device status information"""
    try:
        with get_device_connection(ip, username, password) as net_connect:
            if command.startswith('show vlan'):
                output = get_show_vlan(net_connect, vlan_id)
            elif command.startswith('show ip interface vlan') or command == 'show ip interface brief':
                output = get_show_ip_interface_brief(net_connect, vlan_id)
            else:
                return {
                    'status': 'error',
                    'error': 'Invalid command'
                }
            return {
                'status': 'success',
                'output': output
            }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }