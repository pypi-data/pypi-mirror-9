# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from tasksoftheday import views

urlpatterns = patterns('',
    url(r'^$', views.IndexView.as_view(), name='index'), 
    url(r'^(?P<pk>\d+)/$', views.TaskView.as_view(), name='task'),
    url(r'^newTask/$', views.createTask, name='createTask'),
    url(r'^flip_task_done_status/(?P<task_id>\d+)$', views.flip_task_done_status, name='flip_task_done_status'),
    url(r'^(?P<past_or_future>\past|future)/$', views.TaskListView.as_view(), name='tasklist'),
)