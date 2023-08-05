# -*- coding: utf-8 -*-

import logging
import os

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

import django_rq

from parser import Importer
from forms import ReportForm
from models import Report

# Create the logging instance (spits out to src/EllasKitchen/django.log)
logger = logging.getLogger(__name__)

# DAMN YOU DJANGO RQ
def trigger_queue(obj_id, file):
    Importer(obj_id, file)


@staff_member_required
def import_file(request):

    """
    Imports a CSV or XLS file into the database
    """
    form = ReportForm(request.POST, request.FILES)
    if request.method == 'POST':
        if form.is_valid():
            try:
                report = form.save()
                report_obj = Report.objects.get(id=report.pk)
                report_file = os.path.join(settings.MEDIA_ROOT, report_obj.original_file.name)
                queue = django_rq.get_queue('importer')
                queue.enqueue(trigger_queue, args=(report_obj.id, report_file))
                #queue.enqueue(parser.Importer(report_obj.id, report_file))  # request.FILES['uploadfile']))
                return render_to_response('thanks.html')
            except Exception as e:
                logger.error("CRITICAL ERROR: THE TASK COULDN'T BE EXECUTED.")
                logger.error(e)
        return render_to_response('error.html')
    else:
        return render_to_response('import.html', {'form': form},
                                  context_instance=RequestContext(request))


def list_reports(request):

    """
    List all the reports for the performed imports.
    """
    print "not yet"
