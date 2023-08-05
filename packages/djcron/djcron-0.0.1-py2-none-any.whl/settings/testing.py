from .development import *

SKIP_SOUTH_TESTS = True
SOUTH_TESTS_MIGRATE = False
CELERY_ALWAYS_EAGER = True

MEDIA_ROOT = "/tmp"

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
#INSTALLED_APPS = INSTALLED_APPS + ["tests"]
