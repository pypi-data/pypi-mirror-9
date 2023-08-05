# -*- coding: utf-8 -*-

from django.db import models

STATUS = (
    (0, 'Complete'),
    (1, 'Processing'),
    (2, 'Interrupted'),
    (3, 'Failed'),
)


# class ImportUpload(models.Model):

#     """
#     Fake model to provide a form
#     """
#     email = models.EmailField('E-Mail')
#     uploadfile = models.FileField('File', upload_to='uploads/imports/')
#     pub_date = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = "Import"
#         verbose_name_plural = "Import"
#         get_latest_by = '-pub_date'
#         ordering = ['-pub_date']

#     def __unicode__(self):
#         return self.email


class Report(models.Model):

    """
    This report model is supposed to store the data about the CSV imports
    made into the EK website trough the admin interface.

    Label is a text field that will be edited at will by EK people.

    The amount fields should accept empty values and they should try to store
    a zero if no value is inserted.
    """
    label = models.CharField("Report label", max_length=255, blank=True, null=True)
    email = models.EmailField("Email", blank=True, null=True)
    status = models.PositiveIntegerField("Status", choices=STATUS, blank=True, null=True, default=0)
    total = models.PositiveIntegerField("Total", null=True,
            blank=True, default=0)
    success = models.PositiveIntegerField("Successfully imported", null=True,
              blank=True, default=0)
    failed = models.PositiveIntegerField("Failed", null=True,
             blank=True, default=0)
    original_file = models.FileField("Original file", upload_to="imports/original/", null=True, blank=True)
    failed_records = models.FileField("Failed records", upload_to="imports/", null=True, blank=True)
    existing = models.PositiveIntegerField("Already existed", null=True,
             blank=True, default=0)
    incomplete = models.PositiveIntegerField("Incomplete", null=True,
                 blank=True, default=0)
    pub_date = models.DateTimeField("Imported on", auto_now_add=True)
    mod_date = models.DateTimeField("Modified on", auto_now=True)

    class Meta:
        verbose_name = "Import report"
        verbose_name_plural = "Import reports"
        get_latest_by = '-pub_date'
        ordering = ['-pub_date']

    def __unicode__(self):
        return self.label

