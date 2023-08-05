# -*- coding: utf-8 -*-
import re
import logging
from django import forms
from django.conf import settings
from django.forms.util import ErrorDict
from django.utils.crypto import salted_hmac, constant_time_compare
from django.utils.translation import ugettext_lazy as _

from djcelery import models as djcelery_models
from . import models


LOGGER = logging.getLogger(__name__)


def attrs(**kwargs):
    common = {'class':"form-control"}
    if not kwargs:
        return common
    fixed_kwargs = dict((k.rstrip('_'), v) for k, v in kwargs.items())
    return dict(common.items() + fixed_kwargs.items())


class PeriodicTaskForm(forms.ModelForm):
    class Meta:
        model = djcelery_models.PeriodicTask
        fields = ("name", 'description', 'enabled')
        widgets = {
            'name': forms.TextInput(attrs=attrs()),
            'description': forms.Textarea(attrs=attrs(rows=3)),
            'enabled': forms.CheckboxInput(attrs=attrs()),
        }


class JobForm(forms.Form):
    title = forms.CharField(
        label="Title",
        widget=forms.TextInput(attrs=attrs()),
    )
    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea(attrs=attrs(rows=3)),
    )
    script = forms.CharField(
        label="Script to execute",
        widget=forms.Textarea(attrs=attrs(rows=3)),
    )
    every = forms.CharField(
        label="Every",
        initial=1,
        required=False,
        widget=forms.NumberInput(attrs=attrs()),
        help_text="Explicit perioricity",
    )
    period = forms.CharField(
        label="",
        initial="*",
        required=False,
        widget=forms.Select(choices=djcelery_models.PERIOD_CHOICES,
                            attrs=attrs()),
    )
    crontab = forms.CharField(
        label="Crontab",
        initial="0 * * * *",
        required=False,
        widget=forms.TextInput(attrs=attrs()),
        help_text="Crontab line (m h dow dom mon).",
    )
    mode = forms.CharField(
        label="Select mode",
        initial='I',
        widget=forms.RadioSelect(choices=[('I', 'Interval'), ('C', 'Crontab')],
                                 attrs=attrs(class_='radio')),
        help_text='',
    )
    expires = forms.DateTimeField(
        label='Expires',
        required=False,
        widget=forms.DateTimeInput(attrs=attrs(
            class_='form-control date-picker')),
    )
    enabled = forms.BooleanField(
        label='Enabled',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs=attrs(
            class_='checkbox checkbox-inline')),
    )

    def use_interval(self):
        return self.cleaned_data['mode'] == 'I'

    def use_crontab(self):
        return self.cleaned_data['mode'] == 'C'

    def is_valid(self):
        LOGGER.debug('Checking form validity')
        valid = super(JobForm, self).is_valid()

        if not valid:
            LOGGER.debug('Invalid form! (%s) %s', valid, self._errors)

        if self.use_interval() and not self.cleaned_data['every']:
            LOGGER.debug('Period not set')
            self._errors['every'] = ['You selected period mode,'
                                     ' so the period is mandatory']
            valid = False

        if self.use_crontab and not self.cleaned_data['crontab']:
            LOGGER.debug('Crontab not set')
            self._errors['crontab'] = ['You selected crontab mode,'
                                       ' so the crontab is mandatory']
            valid = False

#        if 'title' in self.cleaned_data:
#            name = self.cleaned_data['title']
#            same_name = djcelery_models.PeriodicTask.objects.filter(name=name)
#            if len(same_name) != 0:
#                LOGGER.debug('Duplicated name')
#                self._errors['title'] = ['Title already exists']
#                valid = False

        return valid
