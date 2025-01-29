from django import forms
from nautobot.dcim.models import Location, DeviceType, Rack
from nautobot.ipam.models import VRF, VLAN, Prefix
from nautobot.extras.models import Tag, Status
from .models import SiteOnboarding, Device
from nautobot.core.forms import DynamicModelMultipleChoiceField
import uuid

class SiteOnboardingForm(forms.ModelForm):
    site_tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        model = SiteOnboarding
        fields = ['name', 'location', 'site_tags']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].queryset = Location.objects.all()

class DeviceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        unused_tag = Tag.objects.get(name="unused")
        active_status = Status.objects.get(name="Active")

        self.fields['rack'].queryset = Rack.objects.filter(tags=unused_tag, status=active_status)
        self.fields['vrfs'].queryset = VRF.objects.filter(tags=unused_tag, status=active_status)

    device_type = forms.ModelChoiceField(queryset=DeviceType.objects.all(), required=True)
    rack = forms.ModelChoiceField(queryset=Rack.objects.all(), required=True)
    vrfs = DynamicModelMultipleChoiceField(queryset=VRF.objects.all(), required=False)
    serial_number = forms.CharField(max_length=100, required=False)

    class Meta:
        model = Device
        fields = ['name', 'device_type', 'rack', 'vrfs', 'serial_number']


from django import forms
from nautobot.ipam.models import VLAN, Prefix
import uuid

class VLANConfigurationForm(forms.Form):
    switch_ip = forms.GenericIPAddressField(
        protocol='IPv4',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Switch IP'})
    )
    vlan = forms.ModelChoiceField(
        queryset=VLAN.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control vlan-select'})
    )
    admin_state = forms.ChoiceField(
        choices=[('no shutdown', 'No Shutdown'), ('shutdown', 'Shutdown')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    vlan_description = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter VLAN Description'})
    )
    subnet = forms.ModelChoiceField(
        queryset=Prefix.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control subnet-select'})
    )
    gateway_ip = forms.GenericIPAddressField(
        protocol='IPv4',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Gateway IP'})
    )
    mtu_size = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter MTU Size'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'vlan' in self.data:
            try:
                vlan_id = uuid.UUID(self.data.get('vlan'))
                self.fields['subnet'].queryset = Prefix.objects.filter(vlan_id=vlan_id)
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Prefix queryset

class MultiVLANConfigurationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = []
        data = kwargs.get('data', None)
        
        if data:
            # Get all unique row indices from the submitted data
            indices = set()
            for key in data.keys():
                if key.startswith('switch_ip_'):
                    index = key.split('_')[-1]
                    indices.add(index)
            
            # Create a form for each row
            for index in indices:
                row_data = {
                    'switch_ip': data.get(f'switch_ip_{index}'),
                    'vlan': data.get(f'vlan_{index}'),
                    'admin_state': data.get(f'admin_state_{index}'),
                    'vlan_description': data.get(f'vlan_description_{index}'),
                    'subnet': data.get(f'subnet_{index}'),
                    'gateway_ip': data.get(f'gateway_ip_{index}'),
                    'mtu_size': data.get(f'mtu_size_{index}')
                }
                row_form = VLANConfigurationForm(row_data)
                self.rows.append(row_form)
        else:
            # Create 3 empty rows for new form
            for _ in range(3):
                self.rows.append(VLANConfigurationForm())

    def is_valid(self):
        return all(row_form.is_valid() for row_form in self.rows)

    def cleaned_data(self):
        return [form.cleaned_data for form in self.rows if form.is_valid()]
    

class ACIConfigForm(forms.Form):
    fabricName = forms.CharField(max_length=100)
    podId = forms.IntegerField()
    nodeId = forms.IntegerField()
    Tenant = forms.CharField(max_length=100)
    AP = forms.CharField(max_length=100)
    EPG = forms.CharField(max_length=100)
    vlan = forms.IntegerField()
    mode = forms.ChoiceField(choices=[('access', 'Access'), ('trunk', 'Trunk')])
    fromPort = forms.IntegerField()
    toPort = forms.IntegerField()