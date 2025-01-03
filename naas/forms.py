from django import forms
from nautobot.dcim.models import Location, DeviceType, Rack
from nautobot.ipam.models import VLAN, Prefix, VRF
from nautobot.extras.models import Tag, Status
from .models import SiteOnboarding
from nautobot.core.forms import DynamicModelMultipleChoiceField

class SiteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        unused_tag = Tag.objects.get(name="unused")
        active_status = Status.objects.get(name="Active")

        self.fields['racks'].queryset = Rack.objects.filter(tags=unused_tag, status=active_status)
        self.fields['vlans'].queryset = VLAN.objects.filter(tags=unused_tag, status=active_status)
        self.fields['prefixes'].queryset = Prefix.objects.filter(tags=unused_tag, status=active_status)
        self.fields['vrfs'].queryset = VRF.objects.filter(tags=unused_tag, status=active_status)

    location = forms.ModelChoiceField(queryset=Location.objects.all(), required=True)
    device_type = forms.ModelChoiceField(queryset=DeviceType.objects.all(), required=True)
    tags = DynamicModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)

    class Meta:
        model = SiteOnboarding
        fields = [
            'name', 'location', 'site_tag', 'device_type', 'tags', 'device_number',
            'num_prefixes_masks', 'racks', 'vlans', 'prefixes', 'vrfs', 'uplink', 'vlan_description'
        ]