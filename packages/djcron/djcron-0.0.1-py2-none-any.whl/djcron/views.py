import re
import logging
from django.shortcuts import redirect
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ValidationError
from django.views.generic.list import ListView
from django.views.generic.edit import DeleteView, CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

import json

from braces.views import LoginRequiredMixin

from djcelery import models as djcelery_models
from . import models, forms


LOGGER = logging.getLogger(__name__)

class CrontabView(LoginRequiredMixin, ListView):
    model = models.Job
    context_object_name = "jobs"


class UpdateCrontabView(LoginRequiredMixin, CreateView, UpdateView):
    model = models.Job
    context_object_name = "jobs"
    form_class = forms.JobForm
    success_url = '/'

    def form_valid(self, form):
        return HttpResponseRedirect('/')

    def get(self, request, pk=None):
        self.object = None
        form_class = self.get_form_class()

        context = self.get_context_data(form=form_class())

        if pk is not None:
            iform = context['form']
            instance = self.model.objects.get(id=pk)
            iform.initial['title'] = instance.periodic_task.name
            iform.initial['description'] = instance.periodic_task.description
            iform.initial['enabled'] = instance.periodic_task.enabled
            iform.initial['expires'] = instance.periodic_task.expires
            iform.initial['script'] = instance.script
            if instance.periodic_task.interval:
                iform.initial['mode'] = 'I'
                iform.initial['every'] = instance.periodic_task.interval.every
                iform.initial['period'] = instance.periodic_task.interval.period
            if instance.periodic_task.crontab:
                iform.initial['mode'] = 'C'
                iform.initial['crontab'] = '{min} {hour} {dow} {dom} {mon}'.format(
                    min=instance.periodic_task.crontab.minute,
                    hour=instance.periodic_task.crontab.hour,
                    dow=instance.periodic_task.crontab.day_of_week,
                    dom=instance.periodic_task.crontab.day_of_month,
                    mon=instance.periodic_task.crontab.month_of_year,
                )
        return self.render_to_response(context)

    def post(self, request, pk=None):
        LOGGER.debug('POST %s', request.path)
        self.object = None

        form = self.get_form_class()(request.POST)
        if not form.is_valid():
            LOGGER.debug('Invalid form:', form._errors)
            return self.form_invalid(form)

        LOGGER.debug('Received valid form')

        interval = None
        crontab = None

        # create interval
        if form.use_interval():
            LOGGER.debug('Creating interval')
            interval, _ = djcelery_models.IntervalSchedule.objects.get_or_create(
                every=form.cleaned_data['every'],
                period=form.cleaned_data['period'],
            )

        # create crontab
        if form.use_crontab():
            LOGGER.debug('Creating crontab')
            str_crontab = form.cleaned_data['crontab']
            minute, hour, dow, dom, mon = re.split('\s+', str_crontab)
            crontab, _ = djcelery_models.CrontabSchedule.objects.get_or_create(
                minute=minute,
                hour=hour,
                day_of_week=dow,
                day_of_month=dom,
                month_of_year=mon,
            )

        name = form.cleaned_data['title']
        description = form.cleaned_data['description']
        enabled = form.cleaned_data['enabled']
        expires = form.cleaned_data['expires']
        script = form.cleaned_data['script']

        if pk is None:
            LOGGER.debug('Creating PeriodicTask')
            periodic_task = djcelery_models.PeriodicTask(
                name=name,
                description=description,
                enabled=enabled,
                task='Cron worker',
                interval=interval,
                crontab=crontab,
                exchange='',
                routing_key='',
                expires=expires,
            )
            periodic_task.save()

            # create job.
            LOGGER.debug('Creating Job')
            job = models.Job(
                periodic_task=periodic_task,
            )
        else:
            LOGGER.debug('Updating Job')
            job = models.Job.objects.get(id=pk)
            periodic_task = job.periodic_task

            periodic_task.name = name
            periodic_task.description = description
            periodic_task.enabled = enabled
            periodic_task.task = 'Cron worker'
            periodic_task.interval = interval
            periodic_task.crontab = crontab
            periodic_task.exchange = ''
            periodic_task.routing_key = ''
            periodic_task.expires = expires

        job.owner = request.user
        job.script = script
        job.save()

        periodic_task.kwargs=json.dumps({'job_id': job.id})
        periodic_task.save()

        LOGGER.debug('Saved!')
        return self.form_valid(form)


class DeleteCrontabView(LoginRequiredMixin, DeleteView):
    model = models.Job

    success_url = reverse_lazy('home')


class DetailCrontabView(LoginRequiredMixin, DetailView):
    model = models.Job
    context_object_name = "job"
#    success_url = reverse_lazy('home')


class DetailExecutionView(LoginRequiredMixin, DetailView):
    model = models.Execution
    context_object_name = "execution"
#    success_url = reverse_lazy('home')
