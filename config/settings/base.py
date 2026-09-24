from pathlib import Path

import environ

# config/settings/base.py -> config/settings -> config -> BASE_DIR (корінь проєкту)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

SITE_URL = env("SITE_URL", default="").rstrip("/")

CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[],
)

R2_ACCESS_KEY_ID = env("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = env("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = env("R2_BUCKET_NAME")
R2_ENDPOINT_URL = env("R2_ENDPOINT_URL")
R2_PUBLIC_HOST = env("R2_PUBLIC_HOST")

INSTALLED_APPS = [
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # local apps
    "apps.core",
    "apps.pages",
    "apps.biography",
    "apps.gallery",
    "apps.videos",
    "apps.media_mentions",
    "apps.memories",
    "apps.seo",
]

MIDDLEWARE = [
    "config.middleware.CanonicalHostMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "config.middleware.AdminUkrainianLocaleMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "config.context_processors.site_settings",
                "config.context_processors.seo_urls",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="5432"),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "uk"

LANGUAGES = [
    ("uk", "Українська"),
    ("en", "English"),
]

MODELTRANSLATION_DEFAULT_LANGUAGE = "uk"

MODELTRANSLATION_LANGUAGES = (
    "uk",
    "en",
)

MODELTRANSLATION_FALLBACK_LANGUAGES = ("uk",)

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

TIME_ZONE = "Europe/Kyiv"
USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/uploads/"
MEDIA_ROOT = BASE_DIR / "media"

VIDEO_UPLOAD_STALE_AFTER_HOURS = env.int(
    "VIDEO_UPLOAD_STALE_AFTER_HOURS",
    default=24,
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
