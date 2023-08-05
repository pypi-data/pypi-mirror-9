# -*- coding: utf-8 -*-

from django.contrib import admin
from django.contrib.admin import DateFieldListFilter

from models import Report


class ReportAdmin(admin.ModelAdmin):

    """
    This shows the administration panel tof the reports. We should show all
    the data to the user, but allow them to only modify the label.
    """
    search_fields = ('label',)
    readonly_fields = ('status', 'success', 'failed', 'existing', 'incomplete',
                       'total', 'original_file', 'pub_date', 'mod_date')
    list_display = ('label', 'total', 'success', 'failed', 'existing',
                    'incomplete', 'pub_date')
    list_filter = (('pub_date', DateFieldListFilter),)

    def has_delete_permission(self, request, obj=None):

        """
        Allow ourselves to delete stuff if needed, but don't allow Ellas Staff.
        """
        if request.user.is_superuser:
            return True
        else:
            return False

    def get_actions(self, request):

        """
        There are some situations where the has_delete_permission function
        won't remove the delete action from the menu. This function will do.
        """
        actions = super(ReportAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions

admin.site.register(Report, ReportAdmin)
