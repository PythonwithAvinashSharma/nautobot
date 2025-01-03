from django.shortcuts import render, redirect
from .forms import SiteForm
from .models import SiteOnboarding
from nautobot.ipam.models import VLAN, VRF, Prefix
from nautobot.dcim.models import Rack
from nautobot.extras.models import Tag

def site_onboarding_view(request):
    if request.method == "POST":
        form = SiteForm(request.POST)
        if form.is_valid():
            site_onboarding = form.save()

            # Update the location to include the new site
            location = site_onboarding.location
            location.sites.add(site_onboarding)

            # Tag the selected VLANs, VRFs, Prefixes, and Racks with the new site and remove the "unused" tag
            unused_tag = Tag.objects.get(name="unused")

            for vlan in site_onboarding.vlans.all():
                vlan.tags.add(site_onboarding)
                vlan.tags.remove(unused_tag)
                vlan.save()

            for vrf in site_onboarding.vrfs.all():
                vrf.tags.add(site_onboarding)
                vrf.tags.remove(unused_tag)
                vrf.save()

            for prefix in site_onboarding.prefixes.all():
                prefix.tags.add(site_onboarding)
                prefix.tags.remove(unused_tag)
                prefix.save()

            for rack in site_onboarding.racks.all():
                rack.tags.add(site_onboarding)
                rack.tags.remove(unused_tag)
                rack.save()

            return redirect('success_url')  # Replace 'success_url' with your success URL
    else:
        form = SiteForm()
    return render(request, 'naas/naas.html', {'form': form})