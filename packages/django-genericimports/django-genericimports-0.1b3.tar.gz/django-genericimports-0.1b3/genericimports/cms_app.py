# -*- coding: utf-8 -*-

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

"""
This file is intended only for django CMS integration. If you add this file
in the APPHOOKS settings dictionary, it will become available as an apphook.
"""


class ImportHubHook(CMSApp):
    name = "User Import Hub"
    urls = ["apps.CustomApphooks.ImportHub.urls"]

apphook_pool.register(ImportHubHook)
