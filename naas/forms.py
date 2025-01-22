from django import forms
from nautobot.dcim.models import Location, DeviceType, Rack
from nautobot.ipam.models import VRF, VLAN, Prefix
from nautobot.extras.models import Tag, Status
from .models import SiteOnboarding, Device
from nautobot.core.forms import DynamicModelMultipleChoiceField

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



class VLANConfigurationForm(forms.ModelForm):
    switch_ip = forms.GenericIPAddressField(protocol='both', unpack_ipv4=False, required=True, label="Switch IP")
    vlan = forms.ModelChoiceField(queryset=VLAN.objects.all(), required=True, label="VLAN")
    admin_state = forms.ChoiceField(choices=[('up', 'Up'), ('down', 'Down')], required=True, label="Admin State")
    vlan_description = forms.CharField(max_length=255, required=False, label="VLAN Description")

    class Meta:
        model = VLAN
        fields = ['switch_ip', 'vlan', 'admin_state', 'vlan_description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vlan'].queryset = VLAN.objects.all()