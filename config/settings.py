from decouple import config
from pathlib import Path
import environ
import os


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environ
env = environ.Env(DEBUG=(bool, False))

# Check if it's a production environment (determine via environment variables)
# Render automatically sets RENDER variables
IS_PRODUCTION = os.environ.get('RENDER') is not None

if IS_PRODUCTION:
    print("Running in PRODUCTION mode, using system environment variables")
else:
    env_file = os.path.join(BASE_DIR, '.env.development')
    if os.path.exists(env_file):
        environ.Env.read_env(env_file)
        print(f"Loaded environment from {env_file}")
    else:
        print("No .env.development file found")

# Use environmental variables
SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
DATABASES = {"default": env.db("DATABASE_URL")}
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party
    "rest_framework_simplejwt.token_blacklist",  # Logout
    "rest_framework",
    "corsheaders",
    # Local apps
    "api",
    # api documentation
    "drf_spectacular",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Django REST Framework (DRF) for Building a RESTful API
REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

"""
Allowing projects to customize the User Model allows for dynamic retrieval of the User Model actually used by the current project, rather than hardcoding specific imports.
"""
AUTH_USER_MODEL = 'api.User'

""" 
API file details settings:

Only add detailed explanations to complex API classes.
@extend_schema(
        summary="Generate custom reports",
        description="This API is quite complex and requires detailed explanation...", 
    )
"""
SPECTACULAR_SETTINGS = {
    'TITLE': 'Lost and Found API',
    'VERSION': '1.0.0',
    # Automatically generated settings (no need to manually add @extend_schema)
    'SCHEMA_PATH_PREFIX': '/api/',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    # Automatically infer tags (based on URL path)
    'TAGS': None,
    
    # Generate description from Serializer help_text
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.hooks.postprocess_schema_enums',
    ],
    
    'ENUM_NAME_OVERRIDES': {},
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'docExpansion': 'list',
    },
}