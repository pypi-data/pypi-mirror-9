DJCron
======

Distributed Cron.

STATUS
------

Still under development, but already usable. Lots of features still to be implemented.

You can try it taking the code from the repository_.

Intention
---------

Cron was created on 70's by Brian Kernighan and it is an awesome tool. But modern systems require more features, because we usually have to deal with farms of computers and dozens of apps.

Our current ``cronjobs`` are getting bigger and bigger, distributed among loads of hosts and we have to manage all of them by hand.

The intention of DJCron is to manage them in an easier way, even leaving the developers to modify them by their own.


Features
--------

- Job creation, update and removal.
- Stats about jobs execution.
- Log all modifications. (TO BE DONE)
- Log-in required.
- Job monitoring and stats (TO BE DONE)
- Distributed, by using message queues. It uses Celery_, so you can configure RabbitMQ_, Redis_ or MongoDB_ as backends).
- Priority management by creating high priority queues and specific workers.
- Web interface, using Django_.



.. _Celery: http://www.celeryproject.org/
.. _RabbitMQ: http://www.rabbitmq.com/
.. _Redis: http://redis.io/
.. _MongoDB: http://www.mongodb.org/
.. _Django: https://www.djangoproject.com/
.. _repository: https://github.com/magmax/djcron


