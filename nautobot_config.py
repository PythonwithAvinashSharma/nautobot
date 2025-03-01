import os
import sys

import os.path
import platform
import re
import tempfile

from django.contrib.messages import constants as messages
import django.forms
from django.utils.safestring import mark_safe
from datetime import timedelta

from nautobot import __version__
from nautobot.core.constants import CONFIG_SETTING_SEPARATOR as _CONFIG_SETTING_SEPARATOR
from nautobot.core.settings_funcs import ConstanceConfigItem, is_truthy, parse_redis_connection
#########################
#                       #
#   Required settings   #
#                       #
#########################

# This is a list of valid fully-qualified domain names (FQDNs) for the Nautobot server. Nautobot will not permit write
# access to the server via any other hostnames. The first FQDN in the list will be treated as the preferred name.
#
# Example: ALLOWED_HOSTS = ['nautobot.example.com', 'nautobot.internal.local']
#
# ALLOWED_HOSTS = os.getenv("NAUTOBOT_ALLOWED_HOSTS", "").split(" ")
AUTH_USER_MODEL = "users.User"

# Set the default AutoField for 3rd party apps
# N.B. Ideally this would be a `UUIDField`, but due to Django restrictions
#      we can't do that yet
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DEBUG = True
ALLOWED_HOSTS = ["*"]
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = '/'  # Redirect after successful login
LOGOUT_REDIRECT_URL = '/'  # Redirect after successful logout

ALLOWED_URL_SCHEMES = [
    "file",
    "ftp",
    "ftps",
    "http",
    "https",
    "irc",
    "mailto",
    "sftp",
    "ssh",
    "tel",
    "telnet",
    "tftp",
    "vnc",
    "xmpp",
    ]

if "NAUTOBOT_BANNER_BOTTOM" in os.environ and os.environ["NAUTOBOT_BANNER_BOTTOM"] != "":
    BANNER_BOTTOM = os.environ["NAUTOBOT_BANNER_BOTTOM"]
if "NAUTOBOT_BANNER_LOGIN" in os.environ and os.environ["NAUTOBOT_BANNER_LOGIN"] != "":
    BANNER_LOGIN = os.environ["NAUTOBOT_BANNER_LOGIN"]
if "NAUTOBOT_BANNER_TOP" in os.environ and os.environ["NAUTOBOT_BANNER_TOP"] != "":
    BANNER_TOP = os.environ["NAUTOBOT_BANNER_TOP"]



EXEMPT_EXCLUDE_MODELS = (
    ("auth", "group"),
    ("users", "user"),
    ("users", "objectpermission"),
)

# Models to exempt from the enforcement of view permissions
EXEMPT_VIEW_PERMISSIONS = []
# The django-redis cache is used to establish concurrent locks using Redis.
#
# CACHES = {
#     "default": {
#         "BACKEND": os.getenv(
#             "NAUTOBOT_CACHES_BACKEND",
#             "django_prometheus.cache.backends.redis.RedisCache" if METRICS_ENABLED else "django_redis.cache.RedisCache",
#         ),
#         "LOCATION": parse_redis_connection(redis_database=1),
#         "TIMEOUT": 300,
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "PASSWORD": "",
#         },
#     }
# }

# Number of seconds to cache ContentType lookups. Set to 0 to disable caching.
# CONTENT_TYPE_CACHE_TIMEOUT = int(os.getenv("NAUTOBOT_CONTENT_TYPE_CACHE_TIMEOUT", "0"))
CONFIG_CONTEXT_DYNAMIC_GROUPS_ENABLED = is_truthy(os.getenv("NAUTOBOT_CONFIG_CONTEXT_DYNAMIC_GROUPS_ENABLED", "False"))



# Database configuration. See the Django documentation for a complete list of available parameters:
#   https://docs.djangoproject.com/en/stable/ref/settings/#databases
#
# DATABASES = {
#     "default": {
#         "NAME": os.getenv("NAUTOBOT_DB_NAME", "nautobot"),  # Database name
#         "USER": os.getenv("NAUTOBOT_DB_USER", ""),  # Database username
#         "PASSWORD": os.getenv("NAUTOBOT_DB_PASSWORD", ""),  # Database password
#         "HOST": os.getenv("NAUTOBOT_DB_HOST", "localhost"),  # Database server
#         "PORT": os.getenv("NAUTOBOT_DB_PORT", ""),  # Database port (leave blank for default)
#         "CONN_MAX_AGE": int(os.getenv("NAUTOBOT_DB_TIMEOUT", "300")),  # Database timeout
#         "ENGINE": os.getenv(
#             "NAUTOBOT_DB_ENGINE",
#             "django_prometheus.db.backends.postgresql" if METRICS_ENABLED else "django.db.backends.postgresql",
#         ),  # Database driver ("mysql" or "postgresql")
#     }
# }

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "nautobot"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "admin12345"),
        "HOST": os.getenv("DB_HOST", "10.24.65.27"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# Ensure proper Unicode handling for MySQL
#
if DATABASES["default"]["ENGINE"].endswith("mysql"):
    DATABASES["default"]["OPTIONS"] = {"charset": "utf8mb4"}

# This key is used for secure generation of random numbers and strings. It must never be exposed outside of this file.
# For optimal security, SECRET_KEY should be at least 50 characters in length and contain a mix of letters, numbers, and
# symbols. Nautobot will not run without this defined. For more information, see
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = os.getenv("NAUTOBOT_SECRET_KEY", "{{ secret_key }}")

SANITIZER_PATTERNS = [
    # General removal of username-like and password-like tokens
    (re.compile(r"(https?://)?\S+\s*@", re.IGNORECASE), r"\1{replacement}@"),
    (
        re.compile(r"(username|password|passwd|pwd|secret|secrets)([\"']?(?:\s+is.?|:)?\s+)\S+[\"']?", re.IGNORECASE),
        r"\1\2{replacement}",
    ),
]

SOCIAL_AUTH_POSTGRES_JSONFIELD = False
# Nautobot related - May be overridden if using custom social auth backend
SOCIAL_AUTH_BACKEND_PREFIX = "social_core.backends"

# Branding logo locations. The logo takes the place of the Nautobot logo in the top right of the nav bar.
# The filepath should be relative to the `MEDIA_ROOT`.
BRANDING_FILEPATHS = {
    "logo": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_LOGO", None),  # Navbar logo
    "favicon": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_FAVICON", None),  # Browser favicon
    "icon_16": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_ICON_16", None),  # 16x16px icon
    "icon_32": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_ICON_32", None),  # 32x32px icon
    "icon_180": os.getenv(
        "NAUTOBOT_BRANDING_FILEPATHS_ICON_180", None
    ),  # 180x180px icon - used for the apple-touch-icon header
    "icon_192": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_ICON_192", None),  # 192x192px icon
    "icon_mask": os.getenv(
        "NAUTOBOT_BRANDING_FILEPATHS_ICON_MASK", None
    ),  # mono-chrome icon used for the mask-icon header
    "header_bullet": os.getenv(
        "NAUTOBOT_BRANDING_FILEPATHS_HEADER_BULLET", None
    ),  # bullet image used for various view headers
    "nav_bullet": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_NAV_BULLET", None),  # bullet image used for nav menu headers
    "css": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_CSS", None),  # Custom global CSS
    "javascript": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_JAVASCRIPT", None),  # Custom global JavaScript
}

# Title to use in place of "Nautobot"
BRANDING_TITLE = os.getenv("NAUTOBOT_BRANDING_TITLE", "Nxt Gen Automation Platform")

# Prepended to CSV, YAML and export template filenames (i.e. `nautobot_device.yml`)
BRANDING_PREPENDED_FILENAME = os.getenv("NAUTOBOT_BRANDING_PREPENDED_FILENAME", "nautobot_")

# Branding URLs (links in the bottom right of the footer)
BRANDING_URLS = {
    "code": os.getenv("NAUTOBOT_BRANDING_URLS_CODE", "https://github.com/nautobot/nautobot"),
    "docs": os.getenv("NAUTOBOT_BRANDING_URLS_DOCS", None),
    "help": os.getenv("NAUTOBOT_BRANDING_URLS_HELP", "https://github.com/nautobot/nautobot/wiki"),
}

# Undocumented link in the bottom right of the footer which is meant to persist any custom branding changes.
BRANDING_POWERED_BY_URL = "https://docs.nautobot.com/"
STRICT_FILTERING = is_truthy(os.getenv("NAUTOBOT_STRICT_FILTERING", "True"))
#
# Django extensions settings
#

# Dont load the 'taggit' app, since we have our own custom `Tag` and `TaggedItem` models
SHELL_PLUS_DONT_LOAD = ["taggit"]
#####################################
#                                   #
#   Optional Django core settings   #
#                                   #
#####################################

# Specify one or more (name, email address) tuples representing Nautobot administrators.
# These people will be notified of application errors (assuming correct email settings are provided).
#
# ADMINS = []

# FQDNs that are considered trusted origins for secure, cross-domain, requests such as HTTPS POST.
# If running Nautobot under a single domain, you may not need to set this variable;
# if running on multiple domains, you *may* need to set this variable to more or less the same as ALLOWED_HOSTS above.
# You also want to set this variable if you are facing CSRF validation issues such as 
# 'CSRF failure has occured' or 'Origin checking failed - https://subdomain.example.com does not match any trusted origins.'
# https://docs.djangoproject.com/en/stable/ref/settings/#csrf-trusted-origins
#
# CSRF_TRUSTED_ORIGINS = []
# if "NAUTOBOT_CSRF_TRUSTED_ORIGINS" in os.environ and os.environ["NAUTOBOT_CSRF_TRUSTED_ORIGINS"] != "":
#    CSRF_TRUSTED_ORIGINS = os.getenv("NAUTOBOT_CSRF_TRUSTED_ORIGINS", "").split(_CONFIG_SETTING_SEPARATOR)

# Date/time formatting. See the following link for supported formats:
# https://docs.djangoproject.com/en/stable/ref/templates/builtins/#date
#
# DATE_FORMAT = os.getenv("NAUTOBOT_DATE_FORMAT", "N j, Y")
# SHORT_DATE_FORMAT = os.getenv("NAUTOBOT_SHORT_DATE_FORMAT", "Y-m-d")
# TIME_FORMAT = os.getenv("NAUTOBOT_TIME_FORMAT", "g:i a")
# DATETIME_FORMAT = os.getenv("NAUTOBOT_DATETIME_FORMAT", "N j, Y g:i a")
# SHORT_DATETIME_FORMAT = os.getenv("NAUTOBOT_SHORT_DATETIME_FORMAT", "Y-m-d H:i")

# Set to True to enable server debugging. WARNING: Debugging introduces a substantial performance penalty and may reveal
# sensitive information about your installation. Only enable debugging while performing testing. Never enable debugging
# on a production system.
#
# DEBUG = is_truthy(os.getenv("NAUTOBOT_DEBUG", "False"))

# If hosting Nautobot in a subdirectory, you must set this value to match the base URL prefix configured in your
# HTTP server (e.g. `/nautobot/`). When not set, URLs will default to being prefixed by `/`.
#
# FORCE_SCRIPT_NAME = None

# IP addresses recognized as internal to the system.
#
# INTERNAL_IPS = ("127.0.0.1", "::1")
PROMETHEUS_EXPORT_MIGRATIONS = False

# Event Brokers
EVENT_BROKERS = {}

#
# Django filters
#

FILTERS_NULL_CHOICE_LABEL = "None"
FILTERS_NULL_CHOICE_VALUE = "null"

STRICT_FILTERING = is_truthy(os.getenv("NAUTOBOT_STRICT_FILTERING", "True"))

#
# Django REST framework (API)
#

VERSION = __version__
REST_FRAMEWORK_VERSION = VERSION.rsplit(".", 1)[0]  # Use major.minor as API version
VERSION_MAJOR, VERSION_MINOR = [int(v) for v in REST_FRAMEWORK_VERSION.split(".")]

REST_FRAMEWORK_ALLOWED_VERSIONS = [f"{VERSION_MAJOR}.{minor}" for minor in range(0, VERSION_MINOR + 1)]


REST_FRAMEWORK = {
    "ALLOWED_VERSIONS": REST_FRAMEWORK_ALLOWED_VERSIONS,
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.SessionAuthentication",
        "nautobot.core.api.authentication.TokenAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "nautobot.core.api.filter_backends.NautobotFilterBackend",
        "nautobot.core.api.filter_backends.NautobotOrderingFilter",
    ),
    "DEFAULT_METADATA_CLASS": "nautobot.core.api.metadata.NautobotMetadata",
    "DEFAULT_PAGINATION_CLASS": "nautobot.core.api.pagination.OptionalLimitOffsetPagination",
    "DEFAULT_PERMISSION_CLASSES": ("nautobot.core.api.authentication.TokenPermissions",),
    "DEFAULT_RENDERER_CLASSES": (
        "nautobot.core.api.renderers.NautobotJSONRenderer",
        "nautobot.core.api.renderers.FormlessBrowsableAPIRenderer",
        "nautobot.core.api.renderers.NautobotCSVRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "nautobot.core.api.parsers.NautobotCSVParser",
    ),
    # Version to use if the client doesn't request otherwise. Default to current (i.e. latest)
    "DEFAULT_VERSION": REST_FRAMEWORK_VERSION,
    "DEFAULT_VERSIONING_CLASS": "nautobot.core.api.versioning.NautobotAPIVersioning",
    "ORDERING_PARAM": "sort",  # This is not meant to be changed by users, but is used internally by the API
    "PAGE_SIZE": None,
    "SCHEMA_COERCE_METHOD_NAMES": {
        # Default mappings
        "retrieve": "read",
        "destroy": "delete",
        # Custom operations
        "bulk_destroy": "bulk_delete",
    },
    "VIEW_NAME_FUNCTION": "nautobot.core.api.utils.get_view_name",
}
# Enable custom logging. Please see the Django documentation for detailed guidance on configuring custom logs:
#   https://docs.djangoproject.com/en/stable/topics/logging/
#
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "normal": {
#             "format": "%(asctime)s.%(msecs)03d %(levelname)-7s %(name)s :\n  %(message)s",
#             "datefmt": "%H:%M:%S",
#         },
#         "verbose": {
#             "format": "%(asctime)s.%(msecs)03d %(levelname)-7s %(name)-20s %(filename)-15s %(funcName)30s() :\n  %(message)s",
#             "datefmt": "%H:%M:%S",
#         },
#     },
#     "handlers": {
#         "normal_console": {
#             "level": "INFO",
#             "class": "logging.StreamHandler",
#             "formatter": "normal",
#         },
#         "verbose_console": {
#             "level": "DEBUG",
#             "class": "logging.StreamHandler",
#             "formatter": "verbose",
#         },
#     },
#     "loggers": {
#         "django": {"handlers": ["normal_console"], "level": "INFO"},
#         "nautobot": {
#             "handlers": ["verbose_console" if DEBUG else "normal_console"],
#             "level": "DEBUG" if DEBUG else "INFO",
#         },
#     },
# }

# Enable the following to setup structlog logging for Nautobot.
# Configures defined loggers to use structlog and overwrites all formatters and handlers.
#
# from nautobot.core.settings_funcs import setup_structlog_logging
# setup_structlog_logging(
#     LOGGING,
#     INSTALLED_APPS,
#     MIDDLEWARE,
#     log_level="DEBUG" if DEBUG else "INFO",
#     debug_db=False,  # Set to True to log all database queries
#     plain_format=bool(DEBUG),  # Set to True to use human-readable structlog format over JSON
# )

# The file path where uploaded media such as image attachments are stored. A trailing slash is not needed.
#

# Set to True to use session cookies instead of persistent cookies.
# Session cookies will expire when a browser is closed.
#
# SESSION_EXPIRE_AT_BROWSER_CLOSE = is_truthy(os.getenv("NAUTOBOT_SESSION_EXPIRE_AT_BROWSER_CLOSE", "False"))

# The length of time (in seconds) for which a user will remain logged into the web UI before being prompted to
# re-authenticate. (Default: 1209600 [14 days])
#
# SESSION_COOKIE_AGE = int(os.getenv("NAUTOBOT_SESSION_COOKIE_AGE", "1209600"))  # 2 weeks, in seconds

# Where Nautobot stores user session data.
#
# SESSION_ENGINE = "django.contrib.sessions.backends.db"

# By default, Nautobot will store session data in the database. Alternatively, a file path can be specified here to use
# local file storage instead. (This can be useful for enabling authentication on a standby instance with read-only
# database access.) Note that the user as which Nautobot runs must have read and write permissions to this path.
#
# SESSION_FILE_PATH = os.getenv("NAUTOBOT_SESSION_FILE_PATH", None)

# Where static files (CSS, JavaScript, etc.) are stored
#

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_URL = "/static/"
STATIC_ROOT = "/home/ubuntu/.nautobot/static"
STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "nautobot/nautobot/project-static"),
        os.path.join(BASE_DIR, 'nautobot/dist'),
]
MEDIA_ROOT =os.path.join(BASE_DIR, "nautobot/media")
GIT_ROOT = os.getenv("NAUTOBOT_GIT_ROOT", os.path.join(BASE_DIR, "git").rstrip("/"))
JOB_FILE_IO_STORAGE = os.getenv("NAUTOBOT_JOB_FILE_IO_STORAGE", "db_file_storage.storage.DatabaseFileStorage")
JOBS_ROOT = os.getenv("NAUTOBOT_JOBS_ROOT", os.path.join(BASE_DIR, "jobs").rstrip("/"))
STORAGE_BACKEND = None
STORAGE_CONFIG = {}
# Plugins
METRICS_DISABLED_APPS = []
PLUGINS =  ["nautobot_device_onboarding", "nautobot_ssot", "nautobot_plugin_nornir", "nautobot_golden_config", "nautobot_firewall_models", "nautobot_device_lifecycle_mgmt", "nautobot_chatops", 
                "dashboard_plugin","nautobot_design_builder", "welcome_wizard", "nautobot_data_validation_engine", "slurpit_nautobot", "nautobot_capacity_metrics", "naas", "nautobot_ui_plugin", "custom_chatbot"]
PLUGINS_CONFIG = {
   "nautobot_plugin_nornir": {
       "use_config_context": {"secrets": True, "connection_options": True},
        # Optionally set global connection options.
        "connection_options": {
            "napalm": {
                "extras": {
                    "optional_args": {"global_delay_factor": 1},
                },
            },
            "netmiko": {
                "extras": {
                    "timeout": 30,
                    "global_delay_factor": 1,
                },
            },
        },
        "nornir_settings": {
            "credentials": "nautobot_plugin_nornir.plugins.credentials.secrets.SecretsCredentials",
            "runner": {
                "plugin": "threaded",
                "options": {
                    "num_workers": 20,
                },
            },
        },
    },
    "nautobot_plugin_device_onboarding": {
        "debug": True,
        "NETWORK_DRIVERS": {
            "default": {
                "netmiko": {"my_network_driver": "cisco_ios"},
                "pyats": {"my_network_driver": "iosxe"},
            },
            "arista": {
                "netmiko": {"my_network_driver": "arista_eos"},
                "pyats": {"my_network_driver": "eos"},
            },
        }
    },
    "nautobot_golden_config": {
        "per_feature_bar_width": 0.15,
        "per_feature_width": 13,
        "per_feature_height": 4,
        "enable_backup": True,
        "enable_compliance": True,
        "enable_intended": True,
        "enable_sotagg": True,
        "enable_plan": True,
        "enable_deploy": True,
        "enable_postprocessing": False,
        "sot_agg_transposer": None,
        "postprocessing_callables": [],
        "postprocessing_subscribed": [],
        "jinja_env": {
            "undefined": "jinja2.StrictUndefined",
            "trim_blocks": True,
            "lstrip_blocks": False,
        },
    "nautobot_firewall_models": {
        "default_status": "Active",
        "allowed_status": ["Active"],
        "capirca_remark_pass": True,
        "capirca_os_map": {
            "cisco_ios": "cisco",
            "arista_eos": "arista",
        },
    }, 
    "nautobot_device_lifecycle_mgmt": {
        "barchart_bar_width": float(os.environ.get("BARCHART_BAR_WIDTH", 0.1)),
        "barchart_width": int(os.environ.get("BARCHART_WIDTH", 12)),
        "barchart_height": int(os.environ.get("BARCHART_HEIGHT", 5)),
    },
    },
    "nautobot_chatops": {
        "fallback_chatops_user": "chatbot",
        "enable_aci": True,
        "aci_creds": {x: os.environ[x] for x in os.environ if "APIC" in x},
        "enable_ansible": True,
        "tower_uri": os.getenv("NAUTOBOT_TOWER_URI"),
        "tower_username": os.getenv("NAUTOBOT_TOWER_USERNAME"),
        "tower_password": os.getenv("NAUTOBOT_TOWER_PASSWORD"),
        "tower_,verify_ssl": is_truthy(os.getenv("NAUTOBOT_TOWER_VERIFY_SSL", "true")),
        "enable_cloudvision": True,
        "aristacv_cvaas_url": os.environ.get("ARISTACV_CVAAS_URL"),
        "aristacv_cvaas_token": os.environ.get("ARISTACV_CVAAS_TOKEN"),
        "aristacv_cvp_host": os.environ.get("ARISTACV_CVP_HOST"),
        # "aristacv_cvp_insecure": is_truthy(os.environ.get("ARISTACV_CVP_INSECURE")),
        "aristacv_cvp_password": os.environ.get("ARISTACV_CVP_PASSWORD"),
        "aristacv_cvp_username": os.environ.get("ARISTACV_CVP_USERNAME"),
        # "aristacv_on_prem": is_truthy(os.environ.get("ARISTACV_ON_PREM")),
    },
    "nautobot_design_builder": {
        "protected_models": [("dcim", "location"), ("dcim", "device")],
        "protected_superuser_bypass": False,
    },
    "welcome_wizard": {
        "enable_devicetype-library": True,
        "enable_welcome_banner": True,
    },
    "nautobot_capacity_metrics": {
        "app_metrics": {
            "gitrepositories": True,
            "jobs": True,
            "models": {
                "dcim": {
                    "Site": True,
                    "Rack": True,
                    "Device": True,
                    "Interface": True,
                    "Cable": True,
                },
                "ipam": {
                    "IPAddress": True,
                    "Prefix": True,
                },
                "extras": {
                    "GitRepository": True
                },
            },
            "queues": True,
            "versions": {
                "basic": True,
                "plugins": True,
            }
        }
    },
    "dashboard_plugin": {},
    "naas": {},
    "custom_chatbot": {},
    "nautobot_data_validation_engine": {},
    "nautobot_ui_plugin" : {},
    # "netbox_topology_views": {
    #     'static_image_directory': 'netbox_topology_views/img',
    #     'allow_coordinates_saving': True,
    #     'always_save_coordinates': True
    # }
}
NETWORK_DRIVERS= {
           "default":{
        "netmiko": {"my_network_driver": "cisco_ios"},
        "pyats": {"my_network_driver": "iosxe"}
    }
}
# DEVICE_USERNAME = os.getenv("DEVICE_USERNAME", "cisco")
# DEVICE_PASS = os.getenv("DEVICE_PASS", "cisco")
# DEVICE_LAB = os.getenv("DEVICE_LAB", "admin")
# DEVICE_PASS = os.getenv("DEVICE_PASS", "C1sco12345")


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # Add your custom templates directory
            os.path.join(BASE_DIR, "/nautobot/core/templates/"),
            os.path.join(BASE_DIR, "/naas/templates/") 
            ],
        'APP_DIRS': True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.media",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
                "social_django.context_processors.login_redirect",
                "nautobot.core.context_processors.settings",
                "nautobot.core.context_processors.sso_auth",
            ],
        },
    },
   {
       "NAME": "jinja",
       "BACKEND": "django_jinja.backend.Jinja2",
       "DIRS": [],
       "APP_DIRS": False,
       "OPTIONS": {
           "context_processors": [
               "django.template.context_processors.debug",
               "django.template.context_processors.request",
               "django.template.context_processors.media",
               "django.contrib.auth.context_processors.auth",
              "django.contrib.messages.context_processors.messages",
               "social_django.context_processors.backends",
               "social_django.context_processors.login_redirect",
               "nautobot.core.context_processors.settings",
               "nautobot.core.context_processors.sso_auth",
           ],
           "environment": "jinja2.sandbox.SandboxedEnvironment",
       },
   },
]

AUTHENTICATION_BACKENDS = [
    # Always check object permissions
    "nautobot.core.authentication.ObjectPermissionBackend",
]
METRICS_ENABLED = is_truthy(os.getenv("NAUTOBOT_METRICS_ENABLED", "False"))
# Internationalization
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_TZ = True

# WSGI
WSGI_APPLICATION = "nautobot.core.wsgi.application"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
X_FRAME_OPTIONS = "DENY"


# Authentication URLs
# This is the URL route name for the login view.
LOGIN_URL = "login"

# This is the URL route name for the home page (index) view.
LOGIN_REDIRECT_URL = "home"

#
# django-constance
#

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_DATABASE_PREFIX = "constance:nautobot:"
CONSTANCE_DATABASE_CACHE_BACKEND = "default"
# Constance defaults to a 24-hour timeout when autofilling its cache, which is undesirable in many cases.
CONSTANCE_DATABASE_CACHE_AUTOFILL_TIMEOUT = int(os.getenv("NAUTOBOT_CACHES_TIMEOUT", "300"))
CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True  # avoid potential errors in a multi-node deployment

# Time zone (default: UTC)
#
# TIME_ZONE = os.getenv("NAUTOBOT_TIME_ZONE", "UTC")

###################################################################
#                                                                 #
#   Optional settings specific to Nautobot and its related apps   #
#                                                                 #
###################################################################

# Allow users to enable request profiling via django-silk for admins to inspect.
# if "NAUTOBOT_ALLOW_REQUEST_PROFILING" in os.environ and os.environ["NAUTOBOT_ALLOW_REQUEST_PROFILING"] != "":
#     ALLOW_REQUEST_PROFILING = is_truthy(os.environ["NAUTOBOT_ALLOW_REQUEST_PROFILING"])

# URL schemes that are allowed within links in Nautobot
#
# ALLOWED_URL_SCHEMES = (
#     "file",
#     "ftp",
#     "ftps",
#     "http",
#     "https",
#     "irc",
#     "mailto",
#     "sftp",
#     "ssh",
#     "tel",
#     "telnet",
#     "tftp",
#     "vnc",
#     "xmpp",
# )

# Banners (HTML is permitted) to display at the top and/or bottom of all Nautobot pages, and on the login page itself.
#
# if "NAUTOBOT_BANNER_BOTTOM" in os.environ and os.environ["NAUTOBOT_BANNER_BOTTOM"] != "":
#     BANNER_BOTTOM = os.environ["NAUTOBOT_BANNER_BOTTOM"]
# if "NAUTOBOT_BANNER_LOGIN" in os.environ and os.environ["NAUTOBOT_BANNER_LOGIN"] != "":
#     BANNER_LOGIN = os.environ["NAUTOBOT_BANNER_LOGIN"]
# if "NAUTOBOT_BANNER_TOP" in os.environ and os.environ["NAUTOBOT_BANNER_TOP"] != "":
#     BANNER_TOP = os.environ["NAUTOBOT_BANNER_TOP"]

# Branding logo locations. The logo takes the place of the Nautobot logo in the top right of the nav bar.
# The filepath should be relative to the `MEDIA_ROOT`.
#
# BRANDING_FILEPATHS = {
#     "logo": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_LOGO", None),  # Navbar logo
#     "favicon": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_FAVICON", None),  # Browser favicon
#     "icon_16": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_ICON_16", None),  # 16x16px icon
#     "icon_32": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_ICON_32", None),  # 32x32px icon
#     "icon_180": os.getenv(
#         "NAUTOBOT_BRANDING_FILEPATHS_ICON_180", None
#     ),  # 180x180px icon - used for the apple-touch-icon header
#     "icon_192": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_ICON_192", None),  # 192x192px icon
#     "icon_mask": os.getenv(
#         "NAUTOBOT_BRANDING_FILEPATHS_ICON_MASK", None
#     ),  # mono-chrome icon used for the mask-icon header
#     "header_bullet": os.getenv(
#         "NAUTOBOT_BRANDING_FILEPATHS_HEADER_BULLET", None
#     ),  # bullet image used for various view headers
#     "nav_bullet": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_NAV_BULLET", None),  # bullet image used for nav menu headers
#     "css": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_CSS", None),  # Custom global CSS
#     "javascript": os.getenv("NAUTOBOT_BRANDING_FILEPATHS_JAVASCRIPT", None),  # Custom global JavaScript
# }

# Prepended to CSV, YAML and export template filenames (i.e. `nautobot_device.yml`)
#
# BRANDING_PREPENDED_FILENAME = os.getenv("NAUTOBOT_BRANDING_PREPENDED_FILENAME", "nautobot_")

# Title to use in place of "Nautobot"
#
# BRANDING_TITLE = os.getenv("NAUTOBOT_BRANDING_TITLE", "Nautobot")

# Branding URLs (links in the bottom right of the footer)
#
# BRANDING_URLS = {
#     "code": os.getenv("NAUTOBOT_BRANDING_URLS_CODE", "https://github.com/nautobot/nautobot"),
#     "docs": os.getenv("NAUTOBOT_BRANDING_URLS_DOCS", None),
#     "help": os.getenv("NAUTOBOT_BRANDING_URLS_HELP", "https://github.com/nautobot/nautobot/wiki"),
# }

# Number of days to retain changelog entries. Set to 0 to retain changes indefinitely. Defaults to 90 if not set here.
#
# if "NAUTOBOT_CHANGELOG_RETENTION" in os.environ and os.environ["NAUTOBOT_CHANGELOG_RETENTION"] != "":
#     CHANGELOG_RETENTION = int(os.environ["NAUTOBOT_CHANGELOG_RETENTION"])

# If True, all origins will be allowed. Other settings restricting allowed origins will be ignored.
# Defaults to False. Setting this to True can be dangerous, as it allows any website to make
# cross-origin requests to yours. Generally you'll want to restrict the list of allowed origins with
# CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGIN_REGEXES.
#
# CORS_ALLOW_ALL_ORIGINS = is_truthy(os.getenv("NAUTOBOT_CORS_ALLOW_ALL_ORIGINS", "False"))

# A list of origins that are authorized to make cross-site HTTP requests. Defaults to [].
#
# CORS_ALLOWED_ORIGINS = [
#     'https://hostname.example.com',
# ]
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "corsheaders",
    "django_filters",
    "django_jinja",
    "django_tables2",
    "django_prometheus",
    "social_django",
    "taggit",
    "timezone_field",
    "nautobot.core.apps.NautobotConstanceConfig",  # overridden form of "constance" AppConfig
    "nautobot.core",
    "django.contrib.admin",  # Must be after `nautobot.core` for template overrides
    "django_celery_beat",  # Must be after `nautobot.core` for template overrides
    "django_celery_results",
    "rest_framework",  # Must be after `nautobot.core` for template overrides
    "db_file_storage",
    "nautobot.circuits",
    #"nautobot_device_onboarding",
    "nautobot.cloud",
    "nautobot.dcim",
    "nautobot.ipam",
    "nautobot.wireless",
    "nautobot.extras",
    "nautobot.tenancy",
    "nautobot.users",
    "nautobot.virtualization",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "graphene_django",
    "health_check",
    "health_check.storage",
    # We have custom implementations of these in nautobot.extras.health_checks:
    # "health_check.db",
    # "health_check.contrib.migrations",
    # "health_check.contrib.redis",
    "django_extensions",
    "django_ajax_tables",
    "silk",
]
MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "silk.middleware.SilkyMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "nautobot.core.middleware.ExceptionHandlingMiddleware",
    "nautobot.core.middleware.RemoteUserMiddleware",
    "nautobot.core.middleware.ExternalAuthMiddleware",
    "nautobot.core.middleware.ObjectChangeMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

MIDDLEWARE.insert(0, "nautobot_design_builder.middleware.GlobalRequestMiddleware")
# A list of strings representing regexes that match Origins that are authorized to make cross-site
# HTTP requests. Defaults to [].
#
# CORS_ALLOWED_ORIGIN_REGEXES = [
#     r'^(https?://)?(\w+\.)?example\.com$',
# ]

# UUID uniquely but anonymously identifying this Nautobot deployment.
#
# if "NAUTOBOT_DEPLOYMENT_ID" in os.environ and os.environ["NAUTOBOT_DEPLOYMENT_ID"] != "":
#     DEPLOYMENT_ID = os.environ["NAUTOBOT_DEPLOYMENT_ID"]

# Device names are not guaranteed globally-unique by Nautobot but in practice they often are.
# Set this to True to use the device name alone as the natural key for Device objects.
# Set this to False to use the sequence (name, tenant, location) as the natural key instead.
#
# if "NAUTOBOT_DEVICE_NAME_AS_NATURAL_KEY" in os.environ and os.environ["NAUTOBOT_DEVICE_NAME_AS_NATURAL_KEY"] != "":
#     DEVICE_NAME_AS_NATURAL_KEY = is_truthy(os.environ["NAUTOBOT_DEVICE_NAME_AS_NATURAL_KEY"])

# Exempt certain models from the enforcement of view permissions. Models listed here will be viewable by all users and
# by anonymous users. List models in the form `<app>.<model>`. Add '*' to this list to exempt all models.
# Defaults to [].
#
# EXEMPT_VIEW_PERMISSIONS = [
#     'dcim.location',
#     'ipam.prefix',
# ]

# Global 3rd-party authentication settings
#
# EXTERNAL_AUTH_DEFAULT_GROUPS = []
# EXTERNAL_AUTH_DEFAULT_PERMISSIONS = {}

# Directory where cloned Git repositories will be stored.
#
# GIT_ROOT = os.getenv("NAUTOBOT_GIT_ROOT", os.path.join(NAUTOBOT_ROOT, "git").rstrip("/"))

# Prefixes to use for custom fields, relationships, and computed fields in GraphQL representation of data.
#
# GRAPHQL_COMPUTED_FIELD_PREFIX = "cpf"
# GRAPHQL_CUSTOM_FIELD_PREFIX = "cf"
# GRAPHQL_RELATIONSHIP_PREFIX = "rel"

# HTTP proxies Nautobot should use when sending outbound HTTP requests (e.g. for webhooks).
#
# HTTP_PROXIES = {
#     'http': 'http://10.10.1.10:3128',
#     'https': 'http://10.10.1.10:1080',
# }

# Send anonymized installation metrics when `nautobot-server post_upgrade` command is run.
#
#INSTALLATION_METRICS_ENABLED = is_truthy(os.getenv("NAUTOBOT_INSTALLATION_METRICS_ENABLED", "{{ installation_metrics_enabled | default(True) }}"))
INSTALLATION_METRICS_ENABLED = is_truthy(os.getenv("NAUTOBOT_INSTALLATION_METRICS_ENABLED", "True"))
MAINTENANCE_MODE = is_truthy(os.getenv("NAUTOBOT_MAINTENANCE_MODE", "False"))
ROOT_URLCONF = "nautobot.core.urls"
# Storage backend to use for Job input files and Job output files.
#
# Note: the default is for backwards compatibility and it is recommended to change it if possible for your deployment.
#
# JOB_FILE_IO_STORAGE = os.getenv("NAUTOBOT_JOB_FILE_IO_STORAGE", "db_file_storage.storage.DatabaseFileStorage")

# Maximum size in bytes of any single file created by Job.create_file().
#
# JOB_CREATE_FILE_MAX_SIZE = 10 << 20

# Directory where Jobs can be discovered.
#
# JOBS_ROOT = os.getenv("NAUTOBOT_JOBS_ROOT", os.path.join(NAUTOBOT_ROOT, "jobs").rstrip("/"))

# Location names are not guaranteed globally-unique by Nautobot but in practice they often are.
# Set this to True to use the location name alone as the natural key for Location objects.
# Set this to False to use the sequence (name, parent__name, parent__parent__name, ...) as the natural key instead.
#
# if "NAUTOBOT_LOCATION_NAME_AS_NATURAL_KEY" in os.environ and os.environ["NAUTOBOT_LOCATION_NAME_AS_NATURAL_KEY"] != "":
#     LOCATION_NAME_AS_NATURAL_KEY = is_truthy(os.environ["NAUTOBOT_LOCATION_NAME_AS_NATURAL_KEY"])

# Log Nautobot deprecation warnings. Note that this setting is ignored (deprecation logs always enabled) if DEBUG = True
#
# LOG_DEPRECATION_WARNINGS = is_truthy(os.getenv("NAUTOBOT_LOG_DEPRECATION_WARNINGS", "False"))

# Setting this to True will display a "maintenance mode" banner at the top of every page.
#
# MAINTENANCE_MODE = is_truthy(os.getenv("NAUTOBOT_MAINTENANCE_MODE", "False"))

# Maximum number of objects that the UI and API will retrieve in a single request. Default is 1000
#
# if "NAUTOBOT_MAX_PAGE_SIZE" in os.environ and os.environ["NAUTOBOT_MAX_PAGE_SIZE"] != "":
#     MAX_PAGE_SIZE = int(os.environ["NAUTOBOT_MAX_PAGE_SIZE"])

# Expose Prometheus monitoring metrics at the HTTP endpoint '/metrics'
#
# METRICS_ENABLED = is_truthy(os.getenv("NAUTOBOT_METRICS_ENABLED", "False"))

# Require API Authentication to HTTP endpoint '/metrics'
#
# METRICS_AUTHENTICATED = is_truthy(os.getenv("NAUTOBOT_METRICS_AUTHENTICATED", "False"))

# Disable app metrics for specific apps
#
# if "NAUTOBOT_METRICS_DISABLED_APPS" in os.environ and os.environ["NAUTOBOT_METRICS_DISABLED_APPS"] != "":
#     METRICS_DISABLED_APPS = os.getenv("NAUTOBOT_METRICS_DISABLED_APPS", "").split(",")

# Credentials that Nautobot will uses to authenticate to devices when connecting via NAPALM.
#
NAPALM_USERNAME = os.getenv("NAUTOBOT_NAPALM_USERNAME", "admin")
NAPALM_PASSWORD = os.getenv("NAUTOBOT_NAPALM_PASSWORD", "C1sco12345")

# NAPALM timeout (in seconds). (Default: 30)
#
# NAPALM_TIMEOUT = int(os.getenv("NAUTOBOT_NAPALM_TIMEOUT", "30"))

# NAPALM optional arguments (see https://napalm.readthedocs.io/en/latest/support/#optional-arguments). Arguments must
# be provided as a dictionary.
#
# NAPALM_ARGS = {}

# Default number of objects to display per page of the UI and REST API. Default is 50
#
# if "NAUTOBOT_PAGINATE_COUNT" in os.environ and os.environ["NAUTOBOT_PAGINATE_COUNT"] != "":
#     PAGINATE_COUNT = int(os.environ["NAUTOBOT_PAGINATE_COUNT"])

# Options given in the web UI for the number of objects to display per page.
# Default is [25, 50, 100, 250, 500, 1000]
#
# if "NAUTOBOT_PER_PAGE_DEFAULTS" in os.environ and os.environ["NAUTOBOT_PER_PAGE_DEFAULTS"] != "":
#     PER_PAGE_DEFAULTS = [int(val) for val in os.environ["NAUTOBOT_PER_PAGE_DEFAULTS"].split(",")]

# Enable installed plugins. Add the name of each plugin to the list.
#
# PLUGINS = []

# Plugins configuration settings. These settings are used by various plugins that the user may have installed.
# Each key in the dictionary is the name of an installed plugin and its value is a dictionary of settings.
#
# PLUGINS_CONFIG = {
#     'my_plugin': {
#         'foo': 'bar',
#         'buzz': 'bazz'
#     }
# }

# Prefer IPv6 addresses or IPv4 addresses in selecting a device's primary IP address? Default False
#
# if "NAUTOBOT_PREFER_IPV4" in os.environ and os.environ["NAUTOBOT_PREFER_IPV4"] != "":
#     PREFER_IPV4 = is_truthy(os.environ["NAUTOBOT_PREFER_IPV4"])

# Default height and width in pixels of a single rack unit in rendered rack elevations. Defaults are 22 and 230
#
# if (
#     "NAUTOBOT_RACK_ELEVATION_DEFAULT_UNIT_HEIGHT" in os.environ
#     and os.environ["NAUTOBOT_RACK_ELEVATION_DEFAULT_UNIT_HEIGHT"] != ""
# ):
#     RACK_ELEVATION_DEFAULT_UNIT_HEIGHT = int(os.environ["NAUTOBOT_RACK_ELEVATION_DEFAULT_UNIT_HEIGHT"])
# if (
#     "NAUTOBOT_RACK_ELEVATION_DEFAULT_UNIT_WIDTH" in os.environ
#     and os.environ["NAUTOBOT_RACK_ELEVATION_DEFAULT_UNIT_WIDTH"] != ""
# ):
#     RACK_ELEVATION_DEFAULT_UNIT_WIDTH = int(os.environ["NAUTOBOT_RACK_ELEVATION_DEFAULT_UNIT_WIDTH"])

# Enable two-digit format for the rack unit numbering in rack elevations.
#
# if (
#     "NAUTOBOT_RACK_ELEVATION_UNIT_TWO_DIGIT_FORMAT" in os.environ
#      and os.environ["NAUTOBOT_RACK_ELEVATION_UNIT_TWO_DIGIT_FORMAT"] != ""
# ):
#     RACK_ELEVATION_UNIT_TWO_DIGIT_FORMAT = is_truthy(os.environ["NAUTOBOT_RACK_ELEVATION_UNIT_TWO_DIGIT_FORMAT"])

# Sets an age out timer of redis lock. This is NOT implicitly applied to locks, must be added
# to a lock creation as `timeout=settings.REDIS_LOCK_TIMEOUT`
#
# REDIS_LOCK_TIMEOUT = int(os.getenv("NAUTOBOT_REDIS_LOCK_TIMEOUT", "600"))
CACHES = {
    "default": {
        "BACKEND": os.getenv(
            "NAUTOBOT_CACHES_BACKEND",
            "django_prometheus.cache.backends.redis.RedisCache" if METRICS_ENABLED else "django_redis.cache.RedisCache",
        ),
        "LOCATION": parse_redis_connection(redis_database=1),
        "TIMEOUT": int(os.getenv("NAUTOBOT_CACHES_TIMEOUT", "300")),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "",
        },
    }
}

CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"
CONSTANCE_DATABASE_PREFIX = "constance:nautobot:"
CONSTANCE_DATABASE_CACHE_BACKEND = "default"
# Constance defaults to a 24-hour timeout when autofilling its cache, which is undesirable in many cases.
CONSTANCE_DATABASE_CACHE_AUTOFILL_TIMEOUT = int(os.getenv("NAUTOBOT_CACHES_TIMEOUT", "300"))
CONSTANCE_IGNORE_ADMIN_VERSION_CHECK = True  # avoid potential errors in a multi-node deployment

CONSTANCE_ADDITIONAL_FIELDS = {
    "per_page_defaults_field": [
        "nautobot.core.forms.fields.JSONArrayFormField",
        {
            "widget": "django.forms.TextInput",
            "base_field": django.forms.IntegerField(min_value=1),
        },
    ],
    "release_check_timeout_field": [
        "django.forms.IntegerField",
        {
            "min_value": 3600,
        },
    ],
    "release_check_url_field": [
        "django.forms.URLField",
        {
            "required": False,
        },
    ],
    "optional_json_field": [
        "django.forms.fields.JSONField",
        {
            "required": False,
        },
    ],
}

CONSTANCE_CONFIG = {
    "ALLOW_REQUEST_PROFILING": ConstanceConfigItem(
        default=False,
        help_text="Allow users to enable request profiling on their login session.",
        field_type=bool,
    ),
    "BANNER_BOTTOM": ConstanceConfigItem(
        default="",
        help_text="Custom Markdown or limited HTML to display in a banner at the bottom of all pages.",
    ),
    "BANNER_LOGIN": ConstanceConfigItem(
        default="",
        help_text="Custom Markdown or limited HTML to display in a banner at the top of the login page.",
    ),
    "BANNER_TOP": ConstanceConfigItem(
        default="",
        help_text="Custom Markdown or limited HTML to display in a banner at the top of all pages.",
    ),
    "CHANGELOG_RETENTION": ConstanceConfigItem(
        default=90,
        help_text="Number of days to retain object changelog history.\nSet this to 0 to retain changes indefinitely.",
        field_type=int,
    ),
    "DEVICE_NAME_AS_NATURAL_KEY": ConstanceConfigItem(
        default=False,
        help_text="Device names are not guaranteed globally-unique by Nautobot but in practice they often are. "
        "Set this to True to use the device name alone as the natural key for Device objects. "
        "Set this to False to use the sequence (name, tenant, location) as the natural key instead.",
        field_type=bool,
    ),
    "DEPLOYMENT_ID": ConstanceConfigItem(
        default="",
        help_text="Randomly generated UUID used to identify this installation.\n"
        "Used for sending anonymous installation metrics, when settings.INSTALLATION_METRICS_ENABLED is set to True.",
        field_type=str,
    ),
    "JOB_CREATE_FILE_MAX_SIZE": ConstanceConfigItem(
        default=10 << 20,
        help_text=mark_safe(  # noqa: S308  # suspicious-mark-safe-usage, but this is a static string so it's safe
            "Maximum size (in bytes) of any single file generated by a <code>Job.create_file()</code> call."
        ),
        field_type=int,
    ),
    "LOCATION_NAME_AS_NATURAL_KEY": ConstanceConfigItem(
        default=False,
        help_text="Location names are not guaranteed globally-unique by Nautobot but in practice they often are. "
        "Set this to True to use the location name alone as the natural key for Location objects. "
        "Set this to False to use the sequence (name, parent__name, parent__parent__name, ...) "
        "as the natural key instead.",
        field_type=bool,
    ),
    "MAX_PAGE_SIZE": ConstanceConfigItem(
        default=1000,
        help_text="Maximum number of objects that a user can list in one UI page or one API call.\n"
        "If set to 0, a user can retrieve an unlimited number of objects.",
        field_type=int,
    ),
    "PAGINATE_COUNT": ConstanceConfigItem(
        default=50,
        help_text="Default number of objects to display per page when listing objects in the UI and/or REST API.",
        field_type=int,
    ),
    "PER_PAGE_DEFAULTS": ConstanceConfigItem(
        default=[25, 50, 100, 250, 500, 1000],
        help_text="Pagination options to present to the user to choose amongst.\n"
        "For proper user experience, this list should include the PAGINATE_COUNT and MAX_PAGE_SIZE values as options.",
        # Use custom field type defined above
        field_type="per_page_defaults_field",
    ),
    "NETWORK_DRIVERS": ConstanceConfigItem(
        default={},
        help_text=mark_safe(  # noqa: S308  # suspicious-mark-safe-usage, but this is a static string so it's safe
            "Extend or override default Platform.network_driver translations provided by "
            '<a href="https://netutils.readthedocs.io/en/latest/user/lib_use_cases_lib_mapper/">netutils</a>. '
            "Enter a dictionary in JSON format, for example:\n"
            '<pre><code class="language-json">{\n'
            '    "netmiko": {"my_network_driver": "cisco_ios"},\n'
            '    "pyats": {"my_network_driver": "iosxe"} \n'
            "}</code></pre>",
        ),
       # Use custom field type defined above
        field_type="optional_json_field",
    ),
    "PREFER_IPV4": ConstanceConfigItem(
        default=False,
        help_text="Whether to prefer IPv4 primary addresses over IPv6 primary addresses for devices.",
        field_type=bool,
    ),
    #"NETWORK_DRIVERS": ConstanceConfigItem(
    #default={
    #    "netmiko": {"my_network_driver": "cisco_ios"},
    #    "pyats": {"my_network_driver": "iosxe"}
    #},
    #help_text=mark_safe(  # noqa: S308  # suspicious-mark-safe-usage, but this is a static string so it's safe
    #    "Extend or override default Platform.network_driver translations provided by "
    #    '<a href="https://netutils.readthedocs.io/en/latest/user/lib_use_cases_lib_mapper/">netutils</a>. '
    #    "Enter a dictionary in JSON format, for example:\n"
    #    '<pre><code class="language-json">{\n'
    #    '    "netmiko": {"my_network_driver": "cisco_ios"},\n'
    #    '    "pyats": {"my_network_driver": "iosxe"} \n'
    #    "}</code></pre>",
    #),
    #field_type="optional_json_field",
    #),
    "RACK_ELEVATION_DEFAULT_UNIT_HEIGHT": ConstanceConfigItem(
        default=22, help_text="Default height (in pixels) of a rack unit in a rack elevation diagram", field_type=int
    ),
    "RACK_ELEVATION_DEFAULT_UNIT_WIDTH": ConstanceConfigItem(
        default=230, help_text="Default width (in pixels) of a rack unit in a rack elevation diagram", field_type=int
    ),
    "RACK_ELEVATION_UNIT_TWO_DIGIT_FORMAT": ConstanceConfigItem(
        default=False,
        help_text="Enables two-digit format for the rack unit numbering in a rack elevation diagram",
        field_type=bool,
    ),
    "RELEASE_CHECK_TIMEOUT": ConstanceConfigItem(
        default=24 * 3600,
        help_text="Number of seconds (must be at least 3600, or one hour) to cache the result of a release check "
        "before checking again for a new release.",
        # Use custom field type defined above
        field_type="release_check_timeout_field",
    ),
    "RELEASE_CHECK_URL": ConstanceConfigItem(
        default="",
        help_text="URL of GitHub repository REST API endpoint to poll periodically for availability of new Nautobot releases.\n"
        'This can be set to the official repository "https://api.github.com/repos/nautobot/nautobot/releases" or '
        "a custom fork.\nSet this to an empty string to disable automatic update checks.",
        # Use custom field type defined above
        field_type="release_check_url_field",
    ),
    "SUPPORT_MESSAGE": ConstanceConfigItem(
        default="",
        help_text="Help message to include on 4xx and 5xx error pages. "
        "Markdown is supported, as are some HTML tags and attributes.\n"
        "If unspecified, instructions to join Network to Code's Slack community will be provided.",
    ),
}

CONSTANCE_CONFIG_FIELDSETS = {
    "Banners": ["BANNER_LOGIN", "BANNER_TOP", "BANNER_BOTTOM"],
    "Change Logging": ["CHANGELOG_RETENTION"],
    "Device Connectivity": ["NETWORK_DRIVERS", "PREFER_IPV4"],
    "Installation Metrics": ["DEPLOYMENT_ID"],
    "Natural Keys": ["DEVICE_NAME_AS_NATURAL_KEY", "LOCATION_NAME_AS_NATURAL_KEY"],
    "Pagination": ["PAGINATE_COUNT", "MAX_PAGE_SIZE", "PER_PAGE_DEFAULTS"],
    "Performance": ["JOB_CREATE_FILE_MAX_SIZE"],
    "Rack Elevation Rendering": [
        "RACK_ELEVATION_DEFAULT_UNIT_HEIGHT",
        "RACK_ELEVATION_DEFAULT_UNIT_WIDTH",
        "RACK_ELEVATION_UNIT_TWO_DIGIT_FORMAT",
    ],
    "Release Checking": ["RELEASE_CHECK_URL", "RELEASE_CHECK_TIMEOUT"],
    "User Interface": ["SUPPORT_MESSAGE"],
    "Debugging": ["ALLOW_REQUEST_PROFILING"],
}



#
# From django-cors-headers
#

# If True, all origins will be allowed. Other settings restricting allowed origins will be ignored.
# Defaults to False. Setting this to True can be dangerous, as it allows any website to make
# cross-origin requests to yours. Generally you'll want to restrict the list of allowed origins with
# CORS_ALLOWED_ORIGINS or CORS_ALLOWED_ORIGIN_REGEXES.
CORS_ALLOW_ALL_ORIGINS = is_truthy(os.getenv("NAUTOBOT_CORS_ALLOW_ALL_ORIGINS", "False"))

# A list of strings representing regexes that match Origins that are authorized to make cross-site
# HTTP requests. Defaults to [].
CORS_ALLOWED_ORIGIN_REGEXES = []

# A list of origins that are authorized to make cross-site HTTP requests. Defaults to [].
CORS_ALLOWED_ORIGINS = []

#
# GraphQL
#

GRAPHENE = {
    "SCHEMA": "nautobot.core.graphql.schema_init.schema",
    "DJANGO_CHOICE_FIELD_ENUM_V3_NAMING": True,  # any field with a name of type will break in Graphene otherwise.
}
GRAPHQL_CUSTOM_FIELD_PREFIX = "cf"
GRAPHQL_RELATIONSHIP_PREFIX = "rel"
GRAPHQL_COMPUTED_FIELD_PREFIX = "cpf"


#
# Caching
#

# The django-redis cache is used to establish concurrent locks using Redis.
CACHES = {
    "default": {
        "BACKEND": os.getenv(
            "NAUTOBOT_CACHES_BACKEND",
            "django_prometheus.cache.backends.redis.RedisCache" if METRICS_ENABLED else "django_redis.cache.RedisCache",
        ),
        "LOCATION": parse_redis_connection(redis_database=1),
        "TIMEOUT": int(os.getenv("NAUTOBOT_CACHES_TIMEOUT", "300")),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "",
        },
    }
}

# Number of seconds to cache ContentType lookups. Set to 0 to disable caching.
CONTENT_TYPE_CACHE_TIMEOUT = int(os.getenv("NAUTOBOT_CONTENT_TYPE_CACHE_TIMEOUT", "0"))

#
# Celery (used for background processing)
#

# Celery Beat heartbeat file path - will be touched by Beat each time it wakes up as a proof-of-health.
CELERY_BEAT_HEARTBEAT_FILE = os.getenv(
    "NAUTOBOT_CELERY_BEAT_HEARTBEAT_FILE",
    os.path.join(tempfile.gettempdir(), "nautobot_celery_beat_heartbeat"),
)

# Celery broker URL used to tell workers where queues are located
CELERY_BROKER_URL = os.getenv("NAUTOBOT_CELERY_BROKER_URL", parse_redis_connection(redis_database=0))

# Celery results backend URL to tell workers where to publish task results - DO NOT CHANGE THIS
CELERY_RESULT_BACKEND = "nautobot.core.celery.backends.NautobotDatabaseBackend"

# Enables extended task result attributes (name, args, kwargs, worker, retries, queue, delivery_info) to be written to backend.
CELERY_RESULT_EXTENDED = True

# A value of None or 0 means results will never expire (depending on backend specifications).
CELERY_RESULT_EXPIRES = None

# Instruct celery to report the started status of a job, instead of just `pending`, `finished`, or `failed`
CELERY_TASK_TRACK_STARTED = True

# If enabled, a `task-sent` event will be sent for every task so tasks can be tracked before they're consumed by a worker.
CELERY_TASK_SEND_SENT_EVENT = True

# How many tasks a worker is allowed to reserve for its own consumption and execution.
# If set to zero (not recommended) a single worker can reserve all tasks even if other workers are free.
# For short running tasks (such as webhooks) you may want to set this to a larger number to increase throughput.
# Conversely, for long running tasks (such as SSoT or Golden-Config Jobs at scale) you may want to set this to 1
# so that a worker executing a long-running task will not prefetch other tasks, which would block their execution
# until the long-running task completes.
# https://docs.celeryq.dev/en/stable/userguide/optimizing.html#prefetch-limits
CELERY_WORKER_PREFETCH_MULTIPLIER = int(os.getenv("NAUTOBOT_CELERY_WORKER_PREFETCH_MULTIPLIER", "4"))

# If enabled stdout and stderr of running jobs will be redirected to the task logger.
CELERY_WORKER_REDIRECT_STDOUTS = is_truthy(os.getenv("NAUTOBOT_CELERY_WORKER_REDIRECT_STDOUTS", "True"))

# The log level of log messages generated by redirected job stdout and stderr.
# Can be one of `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`.
CELERY_WORKER_REDIRECT_STDOUTS_LEVEL = os.getenv("NAUTOBOT_CELERY_WORKER_REDIRECT_STDOUTS_LEVEL", "WARNING")

# Send task-related events so that tasks can be monitored using tools like flower.
# Sets the default value for the workers -E argument.
CELERY_WORKER_SEND_TASK_EVENTS = True

# Default celery queue name that will be used by workers and tasks if no queue is specified
CELERY_TASK_DEFAULT_QUEUE = os.getenv("NAUTOBOT_CELERY_TASK_DEFAULT_QUEUE", "default")

# Global task time limits (seconds)
# Exceeding the soft limit will result in a SoftTimeLimitExceeded exception,
# while exceeding the hard limit will result in a SIGKILL.
CELERY_TASK_SOFT_TIME_LIMIT = int(os.getenv("NAUTOBOT_CELERY_TASK_SOFT_TIME_LIMIT", str(5 * 60)))
CELERY_TASK_TIME_LIMIT = int(os.getenv("NAUTOBOT_CELERY_TASK_TIME_LIMIT", str(10 * 60)))

# Ports for prometheus metric HTTP server running on the celery worker.
# Normally this should be set to a single port, unless you have multiple workers running on a single machine, i.e.
# sharing the same available ports. In that case you need to specify a range of ports greater than or equal to the
# highest amount of workers you are running on a single machine (comma-separated, like "8080,8081,8082"). You can then
# use the `target_limit` parameter to the Prometheus `scrape_config` to ensure you are not getting duplicate metrics in
# that case. Set this to an empty string to disable it.
CELERY_WORKER_PROMETHEUS_PORTS = []
if os.getenv("NAUTOBOT_CELERY_WORKER_PROMETHEUS_PORTS"):
    CELERY_WORKER_PROMETHEUS_PORTS = [
        int(value) for value in os.getenv("NAUTOBOT_CELERY_WORKER_PROMETHEUS_PORTS").split(_CONFIG_SETTING_SEPARATOR)
    ]

# These settings define the custom nautobot serialization encoding as an accepted data encoding format
# and register that format for task input and result serialization
CELERY_ACCEPT_CONTENT = ["nautobot_json"]
CELERY_RESULT_ACCEPT_CONTENT = ["nautobot_json"]
CELERY_TASK_SERIALIZER = "nautobot_json"
CELERY_RESULT_SERIALIZER = "nautobot_json"

CELERY_BEAT_SCHEDULER = "nautobot.core.celery.schedulers:NautobotDatabaseScheduler"

# Sets an age out timer of redis lock. This is NOT implicitly applied to locks, must be added
# to a lock creation as `timeout=settings.REDIS_LOCK_TIMEOUT`
REDIS_LOCK_TIMEOUT = int(os.getenv("NAUTOBOT_REDIS_LOCK_TIMEOUT", "600"))

#
# Custom branding (logo and title)
#

# How frequently to check for a new Nautobot release on GitHub, and the URL to check for this information.
# Defaults to disabled (no URL) and check every 24 hours when enabled
#
# if "NAUTOBOT_RELEASE_CHECK_TIMEOUT" in os.environ and os.environ["NAUTOBOT_RELEASE_CHECK_TIMEOUT"] != "":
#     RELEASE_CHECK_TIMEOUT = int(os.environ["NAUTOBOT_RELEASE_CHECK_TIMEOUT"])
# if "NAUTOBOT_RELEASE_CHECK_URL" in os.environ and os.environ["NAUTOBOT_RELEASE_CHECK_URL"] != "":
#     RELEASE_CHECK_URL = os.environ["NAUTOBOT_RELEASE_CHECK_URL"]

# Remote auth backend settings
#
# REMOTE_AUTH_AUTO_CREATE_USER = False
# REMOTE_AUTH_HEADER = "HTTP_REMOTE_USER"

# Job log entry sanitization and similar
#
# SANITIZER_PATTERNS = [
#     # General removal of username-like and password-like tokens
#     (re.compile(r"(https?://)?\S+\s*@", re.IGNORECASE), r"\1{replacement}@"),
#     (
#         re.compile(r"(username|password|passwd|pwd|secret|secrets)([\"']?(?:\s+is.?|:)?\s+)\S+[\"']?", re.IGNORECASE),
#         r"\1\2{replacement}",
#     ),
# ]

# Configure SSO, for more information see docs/configuration/authentication/sso.md
#
# SOCIAL_AUTH_POSTGRES_JSONFIELD = False

# By default uploaded media is stored on the local filesystem. Using Django-storages is also supported. Provide the
# class path of the storage driver in STORAGE_BACKEND and any configuration options in STORAGE_CONFIG.
# These default to None and {} respectively.
#
# STORAGE_BACKEND = 'storages.backends.s3.S3Storage'
# STORAGE_CONFIG = {
#     'AWS_ACCESS_KEY_ID': 'Key ID',
#     'AWS_SECRET_ACCESS_KEY': 'Secret',
#     'AWS_STORAGE_BUCKET_NAME': 'nautobot',
#     'AWS_S3_REGION_NAME': 'eu-west-1',
# }

# Reject invalid UI/API filter parameters, or discard them while logging a warning?
#
# STRICT_FILTERING = is_truthy(os.getenv("NAUTOBOT_STRICT_FILTERING", "True"))

# Custom message to display on 4xx and 5xx error pages. Markdown and HTML are supported.
# Default message directs the user to #nautobot on NTC's Slack community.
#
# if "NAUTOBOT_SUPPORT_MESSAGE" in os.environ and os.environ["NAUTOBOT_SUPPORT_MESSAGE"] != "":
#     SUPPORT_MESSAGE = os.environ["NAUTOBOT_SUPPORT_MESSAGE"]

# UI_RACK_VIEW_TRUNCATE_FUNCTION
#
# def UI_RACK_VIEW_TRUNCATE_FUNCTION(device_display_name):
#     """Given device display name, truncate to fit the rack elevation view.
#
#     :param device_display_name: Full display name of the device attempting to be rendered in the rack elevation.
#     :type device_display_name: str
#
#     :return: Truncated device name
#     :type: str
#     """
#     return str(device_display_name).split(".")[0]

# A list of strings designating all applications that are enabled in this Django installation.
# Each string should be a dotted Python path to an application configuration class (preferred),
# or a package containing an application.
# https://docs.nautobot.com/projects/core/en/latest/configuration/optional-settings/#extra-applications
# EXTRA_INSTALLED_APPS = []

# Allow users to enable request profiling on their login session
# ALLOW_REQUEST_PROFILING = False
