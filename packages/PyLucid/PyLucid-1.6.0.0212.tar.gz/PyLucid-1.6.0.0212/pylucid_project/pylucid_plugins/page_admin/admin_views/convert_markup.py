# coding: utf-8

"""
    Convert PageContent markup.
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyleft: 2007-2011 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from django import http
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.utils.translation import ugettext as _

from pylucid_project.apps.pylucid.decorators import check_permissions, render_to
from pylucid_project.apps.pylucid.markup import converter, MARKUP_DICT
from pylucid_project.apps.pylucid.markup import hightlighter
from pylucid_project.apps.pylucid.models import PageContent

from page_admin.forms import ConvertMarkupForm


@check_permissions(superuser_only=False, permissions=("pylucid.change_pagecontent",))
@render_to("page_admin/convert_markup.html")
def convert_markup(request, pagecontent_id=None):
    """
    convert a PageContent markup
    """
    if not pagecontent_id:
        raise

    def _error(pagecontent_id, err):
        err_msg = _("Wrong PageContent ID.")
        if settings.DEBUG:
            err_msg += " (ID: %r, original error was: %r)" % (pagecontent_id, err)
        messages.error(request, err_msg)

    try:
        pagecontent_id = int(pagecontent_id)
    except Exception, err:
        return _error(pagecontent_id, err)

    try:
        pagecontent = PageContent.objects.get(id=pagecontent_id)
    except PageContent.DoesNotExist, err:
        return _error(pagecontent_id, err)

    absolute_url = pagecontent.get_absolute_url()
    context = {
        "title": _("Convert '%s' markup") % pagecontent.get_name(),
        "form_url": request.path,
        "abort_url": absolute_url,
        "current_markup": MARKUP_DICT[pagecontent.markup],
        "pagecontent": pagecontent,
    }

    if request.method != "POST":
        form = ConvertMarkupForm(instance=pagecontent)
    else:
        form = ConvertMarkupForm(request.POST, instance=pagecontent)
        #messages.info(request, request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            dest_markup_no = int(cleaned_data["dest_markup"])
            original_markup = cleaned_data["content"]
            try:
                new_markup = converter.convert_markup(
                    original_markup,
                    source_markup_no=pagecontent.markup,
                    dest_markup_no=dest_markup_no,
                    request=request
                )
            except Exception, err:
                messages.error(request, "Convert error: %s" % err)
            else:
                if "preview" not in request.POST:
                    # Save converted markup and redirect to the updated page
                    sid = transaction.savepoint()
                    try:
                        pagecontent.content = new_markup
                        pagecontent.markup = dest_markup_no
                        pagecontent.save()
                    except:
                        transaction.savepoint_rollback(sid)
                        raise
                    else:
                        transaction.savepoint_commit(sid)
                        messages.info(request, _("Content page %r updated.") % pagecontent)
                        return http.HttpResponseRedirect(pagecontent.get_absolute_url())

                # preview markup convert:

                context["new_markup"] = new_markup

                converted_html = converter.apply_markup(
                    new_markup, dest_markup_no, request, escape_django_tags=True
                )
                context["converted_html"] = converted_html

                if cleaned_data["verbose"]:
                    context["original_markup"] = original_markup

                    orig_html = converter.apply_markup(
                        original_markup, pagecontent.markup, request, escape_django_tags=True
                    )
                    context["orig_html"] = orig_html

                    def strip_whitespace(html):
                        return "\n".join([line.strip() for line in html.splitlines() if line.strip()])

                    # Remove whitespace from html code.
                    orig_html2 = strip_whitespace(orig_html)
                    converted_html2 = strip_whitespace(converted_html)

                    if orig_html2 == converted_html2:
                        context["diff_is_the_same"] = True
                    else:
                        context["pygmentize_diff"] = hightlighter.get_pygmentize_diff(orig_html2, converted_html2)

    context.update({
        "form": form,
    })
    return context
