from __future__ import absolute_import

from kombu import Exchange, Queue
from celery import Celery
from django.conf import settings

#BROKER_URL = 'amqp://guest:guest@localhost:5672//'
BROKER_URL = 'redis://localhost/0'
CELERY_RESULT_BACKEND = 'redis://localhost/1'

CELERY_TIMEZONE = 'Europe/Madrid'
CELERY_ENABLE_UTC = True

CELERY_DEFAULT_QUEUE = 'cron'
CELERY_DEFAULT_EXCHANGE = 'cron'
CELERY_DEFAULT_EXCHANGE_TYPE = 'topic'
CELERY_DEFAULT_ROUTING_KEY = 'cron.default'

CELERY_FAST_QUEUE = 'cron.fast'
CELERY_FAST_ROUTING_KEY = 'cron.fast'

CELERY_QUEUES = (
    Queue(CELERY_FAST_QUEUE,
          routing_key=CELERY_FAST_ROUTING_KEY + '.#'),
    Queue(CELERY_DEFAULT_QUEUE,
          routing_key=CELERY_DEFAULT_ROUTING_KEY + '.#'),
)

CELERYBEAT_MAX_LOOP_INTERVAL = 2
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

app = Celery('djcron')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

#app.conf.update(
#    CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
#)



# To use app: from .celery import app as celery_app

## if mod_wsgi:
#import djcelery
#djcelery.setup_loader()

# To run a celery worker:
#    python manage.py celery worker --config=settings --autoreload -B
