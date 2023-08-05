from .common import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

TEMPLATE_CONTEXT_PROCESSORS += [
    "django.core.context_processors.debug",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite'),
    }
}

LOGGING['loggers']['djcron']['level'] = 'DEBUG'
LOGGING['loggers']['django.request']['level'] = 'DEBUG'
