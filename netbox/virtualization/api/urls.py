from __future__ import unicode_literals

from rest_framework import routers

from . import views


class VirtualizationRootView(routers.APIRootView):
    """
    Virtualization API root view
    """
    def get_view_name(self):
        return 'Virtualization'


router = routers.DefaultRouter()
router.APIRootView = VirtualizationRootView

# Clusters
router.register(r'cluster-types', views.ClusterTypeViewSet)
router.register(r'cluster-groups', views.ClusterGroupViewSet)
router.register(r'clusters', views.ClusterViewSet)

# VirtualMachines
router.register(r'virtual-machines', views.VirtualMachineViewSet)
router.register(r'vm-interfaces', views.VMInterfaceViewSet)

app_name = 'virtualization-api'
urlpatterns = router.urls
