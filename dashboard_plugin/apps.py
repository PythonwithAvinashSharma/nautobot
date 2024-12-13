# dashboard_plugin/apps.py
from nautobot.extras.plugins import NautobotAppConfig

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
        from nautobot.extras.plugins.utils import import_object
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Dashboard plugin ready. Checking URLs in {self.__module__}.urls")
        
        # Optional: Import and check if the URLs are being properly loaded
        try:
            import dashboard_plugin.urls  # This ensures the URL configuration is loaded
            logger.info("URLs loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading URLs for {self.verbose_name}: {str(e)}")

config = DashboardPluginConfig