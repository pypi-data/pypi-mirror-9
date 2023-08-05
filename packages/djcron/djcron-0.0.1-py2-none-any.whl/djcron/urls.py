from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.views.generic.base import RedirectView

from . import views


urlpatterns = [
    url(r'^/?$', views.CrontabView.as_view(), name='home'),
    url(r'^job/new/?$', views.UpdateCrontabView.as_view(), name='job_create'),
    url(r'^job/(?P<pk>\d+)/?$', views.DetailCrontabView.as_view(), name='job_detail'),
    url(r'^job/(?P<pk>\d+)/edit/?$', views.UpdateCrontabView.as_view(), name='job_update'),
    url(r'^job/(?P<pk>\d+)/delete/?$', views.DeleteCrontabView.as_view(), name='job_delete'),
    url(r'^execution/(?P<pk>\d+)/?$', views.DetailExecutionView.as_view(), name='execution_detail'),
    url(r'^accounts/login/?$', 'django.contrib.auth.views.login', name='login'),
    url(r'^accounts/logout/?$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^admin/?', include(admin.site.urls)),
]

urlpatterns += staticfiles_urlpatterns(prefix="/static/")

#handler500 = "djcron.base.api.views.api_server_error"
