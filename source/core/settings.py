import os
from pathlib import Path
from decouple import config

# ==============================================================================
# Base Configuration
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=True, cast=bool)

# ==============================================================================
# Cloudflare Turnstile
# ==============================================================================

if DEBUG:
    CLOUDFLARE_TURNSTILE_SITE_KEY = "1x00000000000000000000AA"
    CLOUDFLARE_TURNSTILE_SECRET_KEY = "1x0000000000000000000000000000000AA"
else:
    CLOUDFLARE_TURNSTILE_SITE_KEY = config("CLOUDFLARE_TURNSTILE_SITE_KEY")
    CLOUDFLARE_TURNSTILE_SECRET_KEY = config("CLOUDFLARE_TURNSTILE_SECRET_KEY")

# ==============================================================================
# Allowed Hosts
# ==============================================================================

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="127.0.0.1"
).split(",") + ["testserver"]

# ==============================================================================
# Email Configuration
# ==============================================================================

EMAIL_BACKEND = config("EMAIL_BACKEND")
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT")
EMAIL_USE_TLS = config("EMAIL_USE_TLS")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = config("EMAIL_HOST_USER")

SITE_URL = "http://localhost:8000" if DEBUG else config("SITE_URL")

# ==============================================================================
# Stripe Configuration
# ==============================================================================

STRIPE_SECRET_KEY = config("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = config("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = config("STRIPE_WEBHOOK_SECRET")

# ==============================================================================
# Application Definition
# ==============================================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django_ckeditor_5",
    "captcha",

    # Project Apps
    "branding",
    "home",
    "products",
    "basket",
    "orders",
    "contact",
    "errors",
    "seo",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ==============================================================================
# Security Configuration
# ==============================================================================

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False  # handled by Cloudflare
SECURE_HSTS_SECONDS = 31526000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
USE_X_FORWARDED_HOST = True

# Optional: add production CSRF origins
CSRF_TRUSTED_ORIGINS = [
    "https://lelseasmelts.codeblock.io",
    "https://www.lelseasmelts.codeblock.io",
]

# ==============================================================================
# Caching (Uniform With Codeblock)
# ==============================================================================

if not DEBUG:
    MIDDLEWARE.append("django.middleware.cache.UpdateCacheMiddleware")
    MIDDLEWARE.append("django.middleware.cache.FetchFromCacheMiddleware")

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# ==============================================================================
# URL / Templates
# ==============================================================================

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",

                # App-owned globals
                "branding.context_processors.branding_context",
                "basket.context_processors.basket_context",
                "products.context_processors.product_context",
                "seo.context_processors.seo_meta",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# ==============================================================================
# Database
# ==============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
    if DEBUG
    else {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", "localhost"),
        "PORT": config("DB_PORT", "5432"),
    }
}

# ==============================================================================
# Password Validation
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ==============================================================================
# CKEditor Configuration
# ==============================================================================

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading", "|", "bold", "italic", "underline", "strikethrough",
            "highlight", "|", "link", "removeFormat", "|",
            "bulletedList", "numberedList", "|",
            "blockQuote", "codeBlock", "|",
            "fontColor", "fontSize", "|",
            "insertTable", "imageUpload", "|",
            "fullscreen",
        ],
        "codeBlock": {
            "languages": [
                {"language": "javascript", "label": "JavaScript"},
                {"language": "python", "label": "Python"},
                {"language": "bash", "label": "Bash"},
                {"language": "nginx", "label": "Nginx"},
                {"language": "html", "label": "HTML"},
                {"language": "css", "label": "CSS"},
            ],
        },
    },
}

# ==============================================================================
# Internationalisation
# ==============================================================================

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = False

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==============================================================================
# Static & Media
# ==============================================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
