# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url


urlpatterns = patterns("apps.CustomApphooks.ImportHub.views",
    url(r"^", "import_file"),
    url(r"reports/", "list_reports"),
)
