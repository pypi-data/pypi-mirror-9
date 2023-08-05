from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete

from djcelery import models as djcelery_models


class Job(models.Model):
    periodic_task = models.OneToOneField(
        djcelery_models.PeriodicTask, related_name='+', null=True, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)

    script = models.TextField()

    @property
    def name(self):
        return self.periodic_task.name

    @property
    def description(self):
        return self.periodic_task.description

    @property
    def enabled(self):
        return self.periodic_task.enabled

    @property
    def interval(self):
        return self.periodic_task.interval

    @property
    def crontab(self):
        return self.periodic_task.crontab

    @property
    def expires(self):
        return self.periodic_task.expires

    @property
    def last_run_at(self):
        return self.periodic_task.last_run_at

    @property
    def run_count(self):
        return self.jobs.count()

    @property
    def run_success(self):
        return self.jobs.filter(rc=0).count()

    @property
    def run_failures(self):
        return self.jobs.exclude(rc=0).count()

    @property
    def run_success_average(self):
        total = self.run_count
        return 100 * self.run_success / float(total) if total else 0

    @property
    def run_failure_average(self):
        total = self.run_count
        return 100 * self.run_failures / float(total) if total else 0

    @property
    def executions(self):
        return self.jobs.all()

    def __unicode__(self):
        return str(self.periodic_task.description
                   or self.periodic_task.name)

    def __str__(self):
        return self.__unicode__()


@receiver(post_delete, sender=Job)
def post_delete_job(instance, *args, **kwargs):
    if instance.periodic_task:
        instance.periodic_task.delete()


class Execution(models.Model):
    job = models.ForeignKey(Job, related_name='jobs')

    rc = models.IntegerField(null=True, blank=True)
    stdout = models.TextField(null=True, blank=True)
    stderr = models.TextField(null=True, blank=True)

    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)

    host = models.CharField(max_length=100)

    @property
    def elapsed(self):
        return (self.end - self.start).total_seconds if self.end else ''

    def __unicode__(self):
        return '{host} {start}-{end} {name}'.format(
            name=self.job.name, start=self.start, end=self.end, host=self.host)

    def __str__(self):
        return self.__unicode__()
