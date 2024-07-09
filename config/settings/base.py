from pathlib import Path

import environ
from corsheaders.defaults import default_headers
from django.db import DEFAULT_DB_ALIAS

# General
# ------------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
APPS_DIR = ROOT_DIR / "apps"  # apps/
SECRET_KEY = "django-insecure-kuzm^##r3yo2r&fn@31cde9r0y$gkp6q65c(&rj(sed3iaj+h0"
DEBUG = True
ALLOWED_HOSTS = ["*"]

# Environment Helpers
# ------------------------------------------------------------------------------
env = environ.Env()
env.read_env(str(ROOT_DIR / ".env"))

# Timezone & Localization
# ------------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = False

# Apps
# ------------------------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "django.contrib.humanize", # Handy template tags
    "django.contrib.admin",
    "django.forms",
    "django_crontab",
]
THIRD_PARTY_APPS = [
    # architecture
    "django_celery_beat",
    # cmd functions
    "django_extensions",
    # rest api
    "rest_framework",
    "rest_framework.authtoken",
    # cors & request
    "corsheaders",
    "django_user_agents",
    # azure helpers
    "storages",
    # model helpers
    "phonenumber_field",
    # sendgrid email
    "anymail",
    # CKeditor
    'ckeditor',
    # oauth
    'authlib',
]
CUSTOM_APPS = [
    "apps.azure_media_services",
    "apps.meta",
    "apps.common",
    "apps.learning",
    "apps.access",
    "apps.cms",
    "apps.web_portal",
    "apps.service_idp",
    "apps.my_learnings",
    "apps.purchase",
    "apps.payments",
    "apps.jobs",
    "apps.forums",
    "apps.webinars",
    "apps.hackathons",
    "apps.blogs",
    "apps.ecash",
    "apps.badges"
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

# Middlewares
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    # "apps.common.middlewares.DisableCSRFMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
]

# Urls
# ------------------------------------------------------------------------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
APPEND_SLASH = True

# Templates
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "OPTIONS": {
            "loaders": [
                "django.template.loaders.filesystem.Loader",
                "django.template.loaders.app_directories.Loader",
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
            ],
        },
    }
]

# Static
# ------------------------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = str(ROOT_DIR / "staticfiles")
STATICFILES_DIRS = [str(APPS_DIR / "static")]
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Media
# ------------------------------------------------------------------------------
AZURE_ACCOUNT_KEY = env("DJANGO_AZURE_ACCOUNT_KEY")
AZURE_ACCOUNT_NAME = env("DJANGO_AZURE_ACCOUNT_NAME")
AZURE_CONTAINER = env("DJANGO_AZURE_CONTAINER_NAME")
DEFAULT_FILE_STORAGE = "apps.common.storages.MediaRootAzureStorage"
MEDIA_URL = f"https://{AZURE_ACCOUNT_NAME}.blob.core.windows.net/media/"
MEDIA_ROOT = str(APPS_DIR / "media")
TEMP_ROOT = f"{MEDIA_ROOT}/temp"

# Database & Multi-Tenant
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ROOT_DIR / "db.sqlite3",
    }
}
# DATABASES = {
#     # default database user and credentials | others are added on runtime
#     DEFAULT_DB_ALIAS: {
#         "ENGINE": "mssql",
#         "NAME": env.str("DATABASE_DB", default=""),
#         "USER": env.str("DATABASE_USER", default=""),
#         "PASSWORD": env.str("DATABASE_PASSWORD", default=""),
#         "HOST": env.str("DATABASE_HOST", default=""),
#         "PORT": env.str("DATABASE_PORT", default=""),
#     }
# }

# App Super Admin
# ------------------------------------------------------------------------------
AUTH_USER_MODEL = "access.User"
APP_SUPER_ADMIN = {
    "email": env.str("IDP_ADMIN_USER", default="testadmin@b2c.com"),
    "password": env.str("IDP_ADMIN_PASSWORD", default="7b68d3335dfa4003"),
    "name": env.str("IDP_SUPER_ADMIN_NAME", default="Super Admin"),
}
ADMIN_URL = env.str("DJANGO_ADMIN_URL", default="django-admin/")

# Authentication
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend"
]
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
X_FRAME_OPTIONS = "DENY"
# MANAGERS = [("Ajai Danial", "ajaidanial@gmail.com")]
# ADMINS = MANAGERS
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# CKeditor

BLEACH_ALLOWED_TAGS = [
    'a', 'abbr', 'acronym', 'b', 'br', 'code', 'em', 'i', 
    'strong', 'span', 'ul', 'ol', 'li', 'p', 'h1', 'h2', 
    'h3', 'h4', 'h5', 'h6', 'figure', 'table', 'tr', 'td', 
    'tbody', 'thead', 'th'
]

BLEACH_ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
}

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        # Other CKEditor configurations
    },
}

# Api & Rest Framework
# ------------------------------------------------------------------------------
REST_FRAMEWORK = {
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
        "rest_framework.parsers.MultiPartParser"
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # "rest_framework.authentication.BasicAuthentication",
        # "rest_framework.authentication.SessionAuthentication",
        "apps.access.authentication.AppTokenAuthentication",
    ],
}

PASSWORD_RESET_TIMEOUT = 300

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [*default_headers]

# App Switches
# ------------------------------------------------------------------------------
APP_SWITCHES = {
    # should emails be sent or not
    "SEND_EMAILS": env.bool("SWITCH_SEND_EMAILS", default=True),
    # performance debugging mode
    "DB_DEVELOPER_LOG": env.bool("SWITCH_DB_DEVELOPER_LOG", default=False),
    # periodic tasks debugging mode | call tasks every one minute
    "CELERY_BEAT_DEBUG_MODE": env.bool("SWITCH_CELERY_BEAT_DEBUG_MODE", default=False),
    # supervisor/celery is not running | only django is running, not even cache
    "CELERY_WORKER_DEBUG_MODE": env.bool(
        "SWITCH_CELERY_WORKER_DEBUG_MODE", default=False
    ),
    # redis container is running or not? | use in-memory cache
    "REDIS_CACHE_DEBUG_MODE": env.bool("SWITCH_REDIS_CACHE_DEBUG_MODE", default=False),
}

# CACHES
# ------------------------------------------------------------------------------
if not APP_SWITCHES["REDIS_CACHE_DEBUG_MODE"]:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": env.str("CELERY_BROKER_URL"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": False,
            },
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "unique-snowflake",
        }
    }

# Celery
# ------------------------------------------------------------------------------
if USE_TZ:
    CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# EMAIL
# ------------------------------------------------------------------------------
EMAIL_BACKEND = "anymail.backends.sendgrid.EmailBackend"
EMAIL_SENDER_ADDRESS = env.str("EMAIL_SENDER_ADDRESS", default="noreply@example.com")
EMAIL_SENDER_NAME = env.str("EMAIL_SENDER_NAME", default="App")
EMAIL_SUBJECT_PREFIX = env.str(
    "DJANGO_EMAIL_SUBJECT_PREFIX", default=f"[{EMAIL_SENDER_NAME}]"
)
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = f"'{EMAIL_SENDER_NAME}' <{EMAIL_SENDER_ADDRESS}>"
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_TIMEOUT = 5
ANYMAIL = {
    "SENDGRID_API_KEY": env("SENDGRID_API_KEY"),
    "SENDGRID_API_URL": env("SENDGRID_API_URL", default="https://api.sendgrid.com/v3/"),
}

# Default Overrides
# ------------------------------------------------------------------------------
DATA_UPLOAD_MAX_MEMORY_SIZE = None  # prevents some idiotic upload bug | 500 => 400

# App Configurations
# ------------------------------------------------------------------------------
APP_DATE_FORMAT = "%Y-%m-%d"
APP_TIME_FORMAT = "%H:%M:%S"
APP_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"

# IDP Communication Configuration
# ------------------------------------------------------------------------------
IDP_CONFIG = {
    "host": env.str("IDP_SERVICE_HOST", default="=https://iamserver.azurewebsites.net"),
    "user_create_url": env.str("IDP_USER_CREATE_URL", default=""),
    "authenticate_url" : env.str("IDP_AUTHENTICATE_URL", default=""),
    "logout_url": env.str("IDP_LOGOUT_URL", default=""),
    "change_password_url": env.str("IDP_CHANGE_PASSWORD_URL", default=""),
    "external_reset_password_url": env.str("IDP_EXTERNAL_RESET_PASSWORD_URL", default=""),
    "yaksha_host": env.str("YAKSHA_HOST", default=""),
    "yaksha_assessment_url" : env.str("YAKSHA_ASSESSMENT_URL", default=""),
    "yaksha_assessment_get_url" : env.str("YAKSHA_ASSESSMENT_GET_URL", default=""),
    "yaksha_user_assessment_result_url" : env.str("YAKSHA_USER_ASSESSMENT_RESULT_URL", default=""),
    "mml_host": env.str("MML_HOST", default="https://uat.makemylabs.in"),
    "mml_validate_token_url" : env.str("MML_VALIDATE_TOKEN_URL", default=""),
    "mml_vm_provisioning_url" : env.str("MML_VM_PROVISIONING_URL", default=""),
    "mml_vm_detail_url" : env.str("MML_VM_DETAIL_URL", default=""),
    "mml_status_url": env.str("MML_STATUS", default=""),
    "mml_power_start_url": env.str("MML_POWER_START_URL", default=""),
    "mml_vm_auth_connect": env.str("MML_VM_AUTH_CONNECT", default="")
}

IDP_TENANT_NAME = env.str("IDP_TENANT_NAME", default="")
IDP_TENANT_ID = env.str("IDP_TENANT_ID", default="")
MML_TENANT_ID = env.str("MML_TENANT_ID", default="")

RAZORPAY_KEY_ID = env.str("RAZORPAY_KEY_ID", default="")
RAZORPAY_KEY_SECRET = env.str("RAZORPAY_KEY_SECRET", default="")

# Azure & Services
# ------------------------------------------------------------------------------
AZURE_MS_AAD_TENANT_DOMAIN = env.str("AZURE_MS_AAD_TENANT_DOMAIN", default="")
AZURE_MS_ARM_RESOURCE = env.str("AZURE_MS_ARM_RESOURCE", default="")
AZURE_MS_SUBSCRIPTION_ID = env.str("AZURE_MS_SUBSCRIPTION_ID", default="")
AZURE_MS_STORAGE_ACCOUNT_CONNECTION = env.str(
    "AZURE_MS_STORAGE_ACCOUNT_CONNECTION", default=""
)
AZURE_MS_RESOURCE_GROUP = env.str("AZURE_MS_RESOURCE_GROUP", default="")
AZURE_MS_ACCOUNT_NAME = env.str("AZURE_MS_ACCOUNT_NAME", default="")
AZURE_CLIENT_SECRET = env.str("AZURE_CLIENT_SECRET", default="")
AZURE_TENANT_ID = env.str("AZURE_TENANT_ID", default="")
AZURE_CLIENT_ID = env.str("AZURE_CLIENT_ID", default="")

#Lead Squared Credentials
LEAD_SQUARED_ACCESS_KEY = env.str("LEAD_SQUARED_ACCESS_KEY", default="")
LEAD_SQUARED_SECRET_KEY = env.str("LEAD_SQUARED_SECRET_KEY", default="")
LEAD_SQUARE_HOST = env.str("LEAD_SQUARE_HOST", default="")

# Fontend URL
FRONTEND_WEB_URL = env.str("FRONTEND_WEB_URL", default="")
FRONTEND_CMS_URL = env.str("FRONTEND_CMS_URL", default="")

# Social oauth
AUTHLIB_OAUTH_CLIENTS = {
    # Google
    'google': {
        'client_id': env.str("OAUTH_GOOGLE_CLIENT_ID", default=""),
        'client_secret': env.str("OAUTH_GOOGLE_CLIENT_SECRET", default=""),
        'redirect_uri': env.str("GOOGLE_REDIRECT_URL", default=""),
        'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
        'authorize_params': None,
        'token_url': 'https://accounts.google.com/o/oauth2/token',
        'token_params': None,
        'userinfo_url': 'https://www.googleapis.com/oauth2/v1/userinfo',
        'client_kwargs': {'scope': 'openid profile email'},
    },

    # FaceBook
    'facebook': {
        'client_id': env.str("OAUTH_FACEBOOK_CLIENT_ID", default=""),
        'client_secret': env.str("OAUTH_FACEBOOK_CLIENT_SECRET", default=""),
        'redirect_uri': env.str("FACEBOOK_REDIRECT_URL", default=""),
        'authorize_url': 'https://www.facebook.com/dialog/oauth',
        'token_url': 'https://graph.facebook.com/v12.0/oauth/access_token',
        'userinfo_url': 'https://graph.facebook.com/v12.0/me',
        'client_kwargs': {'scope': 'email public_profile'},
    },

    # LinkedIn
    'linkedin': {
        'client_id': env.str("OAUTH_LINKEDIN_CLIENT_ID", default=""),
        'client_secret': env.str("OAUTH_LINKEDIN_CLIENT_SECRET", default=""),
        'redirect_uri': env.str("LINKEDIN_REDIRECT_URL", default=""),
        'authorize_url': 'https://www.linkedin.com/oauth/v2/authorization',
        'authorize_params': None,
        'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
        'token_params': None,
        'userinfo_url': 'https://api.linkedin.com/v2/me',
        'client_kwargs': {'scope': 'r_liteprofile r_emailaddress'},
    },

    # Microsoft
    'microsoft': {
        'client_id': env.str("OAUTH_MICROSOFT_CLIENT_ID", default=""),
        'client_secret': env.str("OAUTH_MICROSOFT_CLIENT_ID", default=""),
        'redirect_uri': env.str("MICROSOFT_REDIRECT_URL", default=""),
        'authorize_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
        'authorize_params': None,
        'access_token_url': 'https://login.microsoftonline.com/common/oauth2/v2.0/token',
        'access_token_params': None,
        'refresh_token_url': None,
        'client_kwargs': {'scope': 'openid email profile'},
    },
}
