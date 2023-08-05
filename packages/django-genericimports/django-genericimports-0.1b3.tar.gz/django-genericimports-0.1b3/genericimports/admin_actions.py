# -*- coding: utf-8 -*-

"""
This module contains multiple admin actions that are shared across models.
"""


def admin_import(self, request, queryset):

    """
    Ability to import from the administration panel
    """
    pass

admin_import.short_description = "Import users via CSV"
