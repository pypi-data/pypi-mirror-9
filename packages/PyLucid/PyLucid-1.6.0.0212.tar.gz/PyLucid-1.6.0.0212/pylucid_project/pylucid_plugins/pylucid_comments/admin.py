# coding: utf-8

from django.contrib import admin

# https://github.com/jedie/django-reversion-compare
from reversion_compare.admin import CompareVersionAdmin

from pylucid_project.apps.pylucid.base_admin import BaseAdmin

from pylucid_comments.models import PyLucidComment

class PyLucidCommentAdmin(BaseAdmin, CompareVersionAdmin):
    """
    TODO:
        -Add action "set to non public"
        -cut comment text or include it via html "title" tag.
    """
    list_display = (
        'name', "comment",
        #'content_type', 'object_pk',
        "view_on_site_link",
        'ip_address', 'submit_date',
        'is_public', 'is_removed', 'url',
    )
    list_filter = ('submit_date', 'site', 'is_public', 'is_removed', 'content_type')
    date_hierarchy = 'submit_date'
    ordering = ('-submit_date',)
    search_fields = ('comment', 'user__username', 'user_name', 'user_email', 'user_url', 'ip_address')

admin.site.register(PyLucidComment, PyLucidCommentAdmin)
