import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

SECRET_KEY = "5!7p+%-w%dp5&1oq23nz81p18@korjrjajswipi^zv5v#)48fo"

DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = ["192.168.0.200", "serwerxp"]

INSTALLED_APPS = [
    "grappelli.dashboard",
    "grappelli",

    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "crm.admin",
    "crm.contract",
    "crm.customer",
    "crm.date",
    "crm.group",
    "crm.payment",
]

MIDDLEWARE_CLASSES = [
    "django.middleware.cache.UpdateCacheMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    #"django.contrib.auth.middleware.SessionAuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    "django.contrib.messages.context_processors.messages",
]

ROOT_URLCONF = "crm.urls"
WSGI_APPLICATION = "crm.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "crm",
        "USER": "crm",
        "PASSWORD": "5!7p+%-w%dp5",
        "HOST": "localhost",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

LANGUAGE_CODE = "pl"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
CURRENCY = "PLN"
USE_THOUSAND_SEPARATOR = True


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "public", "static")
MEDIA_URL = "/static/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "public", "media")

LOGIN_URL = "/"
GRAPPELLI_ADMIN_TITLE = "Salus per Aquam"
GRAPPELLI_INDEX_DASHBOARD = "crm.admin.dashboard.CRMIndexDashboard"
