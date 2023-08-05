from .testing import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'projectboard',
        'USERNAME': 'postgres',
    }
}
