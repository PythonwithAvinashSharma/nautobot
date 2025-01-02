from django import forms
from .models import SiteOnboarding

class SiteForm(forms.ModelForm):
    class Meta:
        model = SiteOnboarding
        fields = [
            'name', 'location', 'site_tag', 'device_type', 'tags', 'device_number',
            'num_prefixes_masks', 'racks', 'vlan', 'prefix', 'vrf', 'uplink', 'vlan_description'
        ]
        widgets = {
            "tags": forms.CheckboxSelectMultiple(),  # Allows multiple tag selection
        }