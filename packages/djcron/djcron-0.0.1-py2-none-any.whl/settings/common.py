import os.path, sys, os
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

APPEND_SLASH = False
ALLOWED_HOSTS = ["*"]

ADMINS = (
    ("admin", "example@example.org"),
)

LANGUAGES = (
    ("en", _("English")),
    ("es", _("Spanish")),
)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "djcron",
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
]


LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

SITES = {
    "djcron": {"domain": "localhost:8000", "scheme": "http", "name": "api"},
}

SITE_ID = "djcron"

# Session configuration (only used for admin)
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600 # (2 weeks)

# Message System
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# Static url(only if admin is activated).
STATIC_URL = "http://localhost:8000/static/"
ADMIN_MEDIA_PREFIX = "http://localhost:8000/static/admin/"

# Static configuration.
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static', 'vendor', 'bootstrap', 'dist'),
    os.path.join(BASE_DIR, 'static', 'vendor', 'jquery', 'dist'),
    os.path.join(BASE_DIR, 'static', 'vendor', 'jquery-ui'),
    os.path.join(BASE_DIR, 'static', 'vendor', 'jquery-ui', 'themes', 'cupertino'),
)


LOCALE_PATHS = (
    os.path.join(BASE_DIR, "locale"),
)

SECRET_KEY = "8uh192ruhsdiuf1h93r67ger1"


MIDDLEWARE_CLASSES = [
    # Common middlewares
    "django.middleware.common.CommonMiddleware",
    "django.middleware.locale.LocaleMiddleware",

    # Only needed by django admin
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
]

ROOT_URLCONF = "djcron.urls"

TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, "templates"),
]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.admin",
    "django.contrib.staticfiles",

    'djcelery',
    "djmail",

    'djcron',
]

WSGI_APPLICATION = "djcron.wsgi.application"

DJMAIL_REAL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DJMAIL_SEND_ASYNC = True
DJMAIL_MAX_RETRY_NUMBER = 3

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "formatters": {
        "complete": {
            "format": "%(levelname)s:%(asctime)s:%(module)s %(message)s"
        },
        "simple": {
            "format": "%(levelname)s:%(asctime)s: %(message)s"
        },
        "null": {
            "format": "%(message)s",
        },
    },
    "handlers": {
        "null": {
            "level":"DEBUG",
            "class":"django.utils.log.NullHandler",
        },
        "console":{
            "level":"DEBUG",
            "class":"logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "django": {
            "handlers":["null"],
            "propagate": True,
            "level":"INFO",
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "djcron": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        }
    }
}




# NOTE: DON'T INSERT MORE SETTINGS AFTER THIS LINE
TEST_RUNNER="django.test.runner.DiscoverRunner"

if "test" in sys.argv:
    print ("\033[1;91mNo django tests.\033[0m")
    print ("Try: \033[1;33mpy.test\033[0m")
    sys.exit(0)
