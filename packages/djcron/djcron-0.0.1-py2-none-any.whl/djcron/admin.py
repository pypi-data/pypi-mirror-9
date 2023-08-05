from django.contrib import admin

from . import models


class JobAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'owner', 'script')


class ExecutionAdmin(admin.ModelAdmin):
    list_display = ('job', 'host', 'start', 'end', 'elapsed', 'rc')


admin.site.register(models.Job, JobAdmin)
admin.site.register(models.Execution, ExecutionAdmin)
