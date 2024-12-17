# dashboard_plugin/__init__.py
"""App declaration for welcome_wizard."""

from nautobot.apps import NautobotAppConfig

__version__ = "1.0.0"

class DashboardPluginConfig(NautobotAppConfig):
    name = "dashboard_plugin"
    verbose_name = "Dashboard Plugin"
    description = "Custom dashboard for device and KPI health."
    author = "Avinash Sharma"
    author_email = "avinash_sharma@hcltech.com"
    base_url = "dashboard-plugin"
    required_settings = []
    default_settings = {}
    min_version = "1.0.0"
    max_version = "3.0.0"
    caching_config = {}

    def ready(self):
        """Callback when this app is loaded."""
        super().ready()



config = DashboardPluginConfig  # pylint:disable=invalid-name