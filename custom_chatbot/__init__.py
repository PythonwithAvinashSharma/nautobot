# chatbot/__init__.py
"""App declaration for ChatBot."""

from nautobot.apps import NautobotAppConfig

__version__ = "1.0.0"

class CustomChatbotConfig(NautobotAppConfig):
    name = "custom_chatbot"  # Update this to match the name of your app directory
    verbose_name = "Custom Chatbot"  # Update this to match the name of your app
    description = "A custom chatbot for Nautobot."  # Update this to match the description of your app
    author = "Avinash Sharma"  # Update this to match the author of your app
    author_email = "avinash.jecrc@gmail.com"
    base_url = "custom-chatbot"  # Update this to match the URL path of your app
    required_settings = []
    default_settings = {}
    min_version = "1.0.0"
    max_version = "3.0.0"
    caching_config = {}

    def ready(self):
        """Callback when this app is loaded."""
        super().ready()


config = CustomChatbotConfig