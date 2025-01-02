# naas/__init__.py
"""App declaration for NaaS."""

from nautobot.apps import NautobotAppConfig

__version__ = "1.0.0"

class NaaSConfig(NautobotAppConfig):
    name = "naas"
    verbose_name = "NaaS"
    description = "NaaS can replace hardware-centric VPNs, load balancers, firewall appliances, and Multiprotocol Label Switching (MPLS) connections.."
    author = "Avinash Sharma"
    author_email = "avinash_sharma@hcltech.com"
    base_url = "naas"
    required_settings = []
    default_settings = {}
    min_version = "1.0.0"
    max_version = "3.0.0"
    caching_config = {}

    def ready(self):
        """Callback when this app is loaded."""
        super().ready()



config = NaaSConfig