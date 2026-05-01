"""
Django settings for iles_backend project.
Optimized for Enterprise Production & Security.
"""
from datetime import timedelta
from pathlib import Path
import environ
import os

# ============================================================
# ENVIRONMENT & PATH CONFIGURATION
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(
    # Set default values
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["127.0.0.1", "localhost"]),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:3000", "http://127.0.0.1:3000"])
)

# Take environment variables from .env file (if it exists)
environ.Env.read_env(BASE_DIR / '.env')

# ============================================================
# CORE SECURITY SETTINGS
# ============================================================
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY", default="django-insecure-0$3evd^y0l88pon-l(__p+wk@#8+j0g%224syl_pw%szznz+6l")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# ============================================================
# APPLICATION DEFINITION
# ============================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # WhiteNoise must be placed before staticfiles in some edge cases
    "whitenoise.runserver_nostatic", 
    "django.contrib.staticfiles",
    
    # Third-party Apps
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "simple_history",
    
    # Internal Apps
    "users.apps.UsersConfig",
    "issues.apps.IssuesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise sits right behind SecurityMiddleware to serve static files instantly
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # CORS must be placed BEFORE CommonMiddleware
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ROOT_URLCONF = "core.urls"

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

WSGI_APPLICATION = "core.wsgi.application"

# ============================================================
# DATABASE
# ============================================================
# Reads from DATABASE_URL in your .env file, falls back to default if missing
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default="postgres://ilesuser:2026@iles@localhost:5432/iles2026"
    )
}

# ============================================================
# CUSTOM AUTHENTICATION
# ============================================================
AUTH_USER_MODEL = "users.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ============================================================
# REST FRAMEWORK & API SETTINGS
# ============================================================
REST_FRAMEWORK = {
    # 1. Deny access by default unless explicitly allowed in the ViewSet
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # 2. Tell DRF to look for JWT Bearer tokens in the request headers
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    # 3. Hook up the Auto-Documentation engine
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# ============================================================
# JWT (JSON WEB TOKEN) CONFIGURATION
# ============================================================
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
}

# ============================================================
# OPENAPI DOCUMENTATION SETTINGS
# ============================================================
SPECTACULAR_SETTINGS = {
    "TITLE": "ILES1 Backend API",
    "DESCRIPTION": "Internship Learning Evaluation System API Documentation",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ============================================================
# CORS (CROSS-ORIGIN RESOURCE SHARING)
# ============================================================
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
CORS_ALLOW_CREDENTIALS = True

# ============================================================
# INTERNATIONALIZATION & STATIC FILES
# ============================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Kampala"  # Set to East African Time
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Enable gzip compression and caching for static files in production
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================================
# EMAIL SETTINGS
# ============================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
# Optional: The name that shows up as the sender
DEFAULT_FROM_EMAIL = f"I.L.E.S. Portal <{EMAIL_HOST_USER}>"