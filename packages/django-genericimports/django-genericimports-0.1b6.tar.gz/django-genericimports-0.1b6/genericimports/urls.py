# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns('',
    url(r"^", views.import_file),
    url(r"reports/", views.list_reports),
)
