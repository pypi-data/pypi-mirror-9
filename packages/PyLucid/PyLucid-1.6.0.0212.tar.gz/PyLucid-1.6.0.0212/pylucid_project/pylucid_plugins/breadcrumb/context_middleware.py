# -*- coding: utf-8 -*-

"""
    PyLucid breadcrumb plugin
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Generates a horizontal backlink bar.

    Last commit info:
    ~~~~~~~~~
    $LastChangedDate: $
    $Rev: $
    $Author: JensDiemer $

    :copyleft: 2009 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details
"""

__version__ = "$Rev:$"

from django.template import RequestContext
from django.shortcuts import render_to_response

from pylucid_project.apps.pylucid.models import PageTree

from breadcrumb.preference_forms import BreadcumbPrefForm


class ContextMiddleware(object):
    def __init__(self, request):
        self.request = request

        self.linklist = []

    def add_link(self, name, title="", url=None):
        """
        Can be called from plugins, to insert own virtual sub pages.
        if url==None: use full current request path
        """
        url = url or self.request.get_full_path()
        self.linklist.append({"name": name, "title": title, "url": url})

    def render(self):
        # Get preferences
        pref_form = BreadcumbPrefForm()
        pref_data = pref_form.get_preferences()

        # Get all pages back to the root page as a list
        linklist = PageTree.objects.get_backlist(self.request)
        linklist += self.linklist

        context = {
            "preferences": pref_data,
            "linklist": linklist,
        }
        return render_to_response('breadcrumb/breadcrumb.html', context,
            context_instance=RequestContext(self.request)
        )
