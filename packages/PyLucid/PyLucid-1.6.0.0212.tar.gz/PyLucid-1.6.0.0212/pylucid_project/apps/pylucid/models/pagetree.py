# coding: utf-8


"""
    PyLucid models
    ~~~~~~~~~~~~~~

    :copyleft: 2009-2013 by the PyLucid team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import sys


from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.http import Http404
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

# http://code.google.com/p/django-tools/
from django_tools import model_utils
from django_tools.local_sync_cache.local_sync_cache import LocalSyncCache
from django_tools.middlewares import ThreadLocal
from django_tools.models import UpdateInfoBaseModel

from pylucid_project.apps.pylucid.tree_model import BaseTreeModel, TreeGenerator
from pylucid_project.base_models.base_models import BaseModelManager, BaseModel
from pylucid_project.base_models.permissions import PermissionsBase
from pylucid_project.apps.pylucid.signals_handlers import update_plugin_urls


TAG_INPUT_HELP_URL = \
"http://google.com/search?q=cache:django-tagging.googlecode.com/files/tagging-0.2-overview.html#tag-input"


class PageTreeManager(BaseModelManager):
    """
    Manager class for PageTree model

    inherited from models.Manager:
        get_or_create() method, witch expected a request object as the first argument.
    """
    def filter_accessible(self, queryset, user):
        """
        exclude form pagetree queryset all pages which the given user can't see
        by checking PageTree.permitViewGroup
        TODO: Check in unittests
        """
        if user.is_anonymous():
            # Anonymous user are in no user group
            return queryset.filter(permitViewGroup__isnull=True)

        if user.is_superuser:
            # Superuser can see everything ;)
            return queryset

        # filter pages for authenticated,normal users

        user_groups = user.groups.values_list('pk', flat=True)

        if not user_groups:
            # User is in no group
            return queryset.filter(permitViewGroup__isnull=True)

        # Filter out all view group
        return queryset.filter(
            models.Q(permitViewGroup__isnull=True) | models.Q(permitViewGroup__in=user_groups)
        )

    def all_accessible(self, user=None, filter_showlinks=False):
        """ returns a PageTree queryset with all items that the given user can access. """
        if user == None:
            user = ThreadLocal.get_current_user()

        queryset = self.model.on_site.order_by("position")
        queryset = self.filter_accessible(queryset, user)

        if filter_showlinks:
            # Filter PageTree.showlinks
            queryset = queryset.filter(showlinks=True)

        return queryset

    def get_tree(self, user=None, filter_showlinks=False, exclude_plugin_pages=False, exclude_extras=None):
        """ return a TreeGenerator instance with all accessable page tree instance """
        queryset = self.all_accessible(user, filter_showlinks)

        if exclude_plugin_pages:
            queryset = queryset.exclude(page_type=PageTree.PLUGIN_TYPE)
        if exclude_extras:
            queryset = queryset.exclude(**exclude_extras)

        items = queryset.values("id", "parent", "slug")
        tree = TreeGenerator(items, skip_no_parent=True)
        return tree

    def get_choices(self, user=None, exclude_extras=None):
        """ returns a choices list for e.g. a forms select widget. """
        tree = PageTree.objects.get_tree(user, exclude_plugin_pages=True, exclude_extras=exclude_extras)
        choices = [("", "---------")] + [
            (node.id, node.get_absolute_url()) for node in tree.iter_flat_list()
        ]
        return choices

    def get_root_page(self, user, filter_parent=True):
        """ returns the 'first' root page tree entry witch the user can access """
        queryset = self.all_accessible(user)

        if filter_parent:
            # All "root" pages
            queryset = queryset.filter(parent=None)
        else:
            # fallback if no "root" page is accessable
            queryset = queryset.order_by("parent", "position")

        try:
            return queryset[0]
        except IndexError, err:
            if self.model.on_site.count() == 0:
                raise PageTree.DoesNotExist("There exist no PageTree items!")
            elif filter_parent == True:
                # If all root pages not accessible for the current user
                # -> try to get the first accessable page
                return self.get_root_page(user, filter_parent=False)
            else:
                raise

    def get_pagemeta(self, request, pagetree, show_lang_errors=True):
        """
        return PageMeta instance witch associated to the given >pagetree< instance.
        
        raise PermissionDenied if current user hasn't the pagemeta.permitViewGroup permissions. 
        
        dissolving language in client favored languages
        if not exist:
            return system default language
            
        If show_lang_errors==True:
            create a page_msg if PageMeta doesn't exist in client favored language.
        """
        from pylucid_project.apps.pylucid.models import PageMeta # against import loops.

        # client favored Language instance:
        lang_entry = request.PYLUCID.current_language

        if pagetree.page_type == pagetree.PLUGIN_TYPE:
            # Automatic create a not existing PageMeta on PluginPages
            pagemeta = PageMeta.objects.verbose_get_or_create(
                request, pagetree, lang_entry, show_lang_errors=show_lang_errors
            )
            return pagemeta

        queryset = PageMeta.objects.filter(pagetree=pagetree)
        pagemeta, tried_languages = self.get_by_prefered_language(request, queryset, show_lang_errors=show_lang_errors)

        if pagemeta is None:
            msg = ""
            if settings.DEBUG:
                msg += "This page %r doesn't exist in any languages???" % pagetree
            raise Http404(msg)

        if tried_languages and show_lang_errors and (settings.DEBUG or request.user.is_authenticated()):
            # We should not inform anonymous user, because the page
            # would not caches, if messages exist!
            messages.info(request,
                _(
                    "PageMeta %(slug)s doesn't exist in client"
                    " favored language %(tried_languages)s,"
                    " use %(used_code)s entry."
                ) % {
                    "slug": pagetree.slug,
                    "tried_languages": ", ".join([l.description for l in tried_languages]),
                    "used_code": pagemeta.language.description,
                }
            )

        # Check PageMeta.permitViewGroup permissions:
        # TODO: Check this in unittests!
        if pagemeta.permitViewGroup == None:
            # everyone can't see this page
            return pagemeta
        elif request.user.is_superuser: # Superuser can see everything ;)
            return pagemeta
        elif request.user.is_authenticated() and pagemeta.permitViewGroup in request.user.groups:
            return pagemeta

        # The user is anonymous or is authenticated but is not in the right user group
        raise PermissionDenied

    def get_backlist(self, request, pagetree=None):
        """
        Generate a list of backlinks, usefull for generating a "You are here" breadcrumb navigation.
        TODO: filter showlinks and permit settings
        TODO: filter current site
        FIXME: Think this created many database requests
        """
        if pagetree == None:
            pagetree = request.PYLUCID.pagetree

        pagemeta = self.get_pagemeta(request, pagetree, show_lang_errors=False)
        url = pagemeta.get_absolute_url()
        page_name = pagemeta.get_name()
        page_title = pagemeta.get_title()

        backlist = [{"url": url, "name": page_name, "title": page_title}]

        parent = pagetree.parent
        if parent:
            # insert parent links
            backlist = self.get_backlist(request, parent) + backlist

        return backlist


class PageTree(BaseModel, BaseTreeModel, UpdateInfoBaseModel, PermissionsBase):
    """
    The CMS page tree

    inherited attributes from TreeBaseModel:
        parent
        position

    inherited attributes from UpdateInfoBaseModel:
        createtime     -> datetime of creation
        lastupdatetime -> datetime of the last change
        createby       -> ForeignKey to user who creaded this entry
        lastupdateby   -> ForeignKey to user who has edited this entry
        
    inherited from PermissionsBase:
        validate_permit_group()
        check_sub_page_permissions()
    """
    PAGE_TYPE = 'C'
    PLUGIN_TYPE = 'P'

    TYPE_CHOICES = (
        (PAGE_TYPE, 'CMS-Page'),
        (PLUGIN_TYPE , 'PluginPage'),
    )
    TYPE_DICT = dict(TYPE_CHOICES)

    objects = PageTreeManager()

    slug = models.SlugField(unique=False, help_text="(for building URLs)")

    site = models.ForeignKey(Site, default=Site.objects.get_current)
    on_site = CurrentSiteManager()

    page_type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    design = models.ForeignKey("pylucid.Design", help_text="Page Template, CSS/JS files")

    showlinks = models.BooleanField(default=True,
        help_text="Accessable for all users, but don't put a Link to this page into menu/sitemap etc."
    )
    permitViewGroup = models.ForeignKey(Group, related_name="%(class)s_permitViewGroup",
        help_text="Limit viewable to a group?",
        null=True, blank=True,
    )
    permitEditGroup = models.ForeignKey(Group, related_name="%(class)s_permitEditGroup",
        help_text="Usergroup how can edit this page.",
        null=True, blank=True,
    )

    def clean_fields(self, exclude):
        """
        We must call clean_slug() here, because it needs a queryset. 
        """
        # check if parent is the same entry: child <-> parent loop:
        super(PageTree, self).clean_fields(exclude)

        message_dict = {}

        # Check if slug exist in the same sub tree:
        if "slug" not in exclude:
            if self.parent == None: # parent is the tree root
                if self.slug in settings.SLUG_BLACKLIST:
                    # e.g. /media/ or /pylucid_admin/
                    msg = (
                        "Sorry, page slug '/<strong>%s</strong>/' is not usable!"
                        " (Not usable slugs are: %s)"
                    ) % (self.slug, ", ".join(settings.SLUG_BLACKLIST))
                    message_dict["slug"] = (mark_safe(msg),)

            queryset = PageTree.on_site.filter(slug=self.slug, parent=self.parent)

            # Exclude the current object from the query if we are editing an
            # instance (as opposed to creating a new one)
            if self.pk is not None:
                queryset = queryset.exclude(pk=self.pk)

            exists = queryset.count()
            if exists:
                if self.parent == None: # parent is the tree root
                    parent_url = "/"
                else:
                    parent_url = self.parent.get_absolute_url()

                msg = "Page '%s<strong>%s</strong>/' exists already." % (parent_url, self.slug)
                message_dict["slug"] = (mark_safe(msg),)

        # Check if parent page is a ContentPage, a plugin page can't have any sub pages!
        if "parent" not in exclude and self.parent is not None and self.parent.page_type != self.PAGE_TYPE:
            parent_url = self.parent.get_absolute_url()
            msg = _(
                "Can't use the <strong>plugin</strong> page '%s' as parent page!"
                " Please choose a <strong>content</strong> page."
            ) % parent_url
            message_dict["parent"] = (mark_safe(msg),)

        # Prevents that a unprotected page created below a protected page.
        # TODO: Check this in unittests
        # validate_permit_group() method inherited from PermissionsBase
        self.validate_permit_group("permitViewGroup", exclude, message_dict)
        self.validate_permit_group("permitEditGroup", exclude, message_dict)

        # Warn user if PageTree permissions mismatch with sub pages
        # TODO: Check this in unittests
        queryset = PageTree.objects.filter(parent=self)
        self.check_sub_page_permissions(# method inherited from PermissionsBase
            ("permitViewGroup", "permitEditGroup"),
            exclude, message_dict, queryset
        )

        if message_dict:
            raise ValidationError(message_dict)

    def recusive_attribute(self, attribute):
        """
        Goes the pagetree back to root and return the first match of attribute if not None.
        
        used e.g.
            with permitViewGroup and permitEditGroup
            from self.validate_permit_group() and self.check_sub_page_permissions()
        """
        parent = self.parent
        if parent is None: # parent is the tree root
            return None

        if getattr(parent, attribute) is not None:
            # the attribute was set by parent page
            return parent
        else:
            # go down to root
            return parent.recusive_attribute(attribute)

    _url_cache = LocalSyncCache(id="PageTree_absolute_url")
    def get_absolute_url(self):
        """ absolute url *without* language code (without domain/host part) """
        try:
            url = self._url_cache[self.pk]
            # print "PageTree url cache len: %s, pk: %s" % (len(self._url_cache), self.pk)
        except KeyError:
            if self.parent:
                parent_shortcut = self.parent.get_absolute_url()
                url = parent_shortcut + self.slug + "/"
            else:
                url = "/" + self.slug + "/"

            self._url_cache[self.pk] = url
        return url

    def get_absolute_uri(self):
        """ absolute url with domain/host part (but without language code) """
        absolute_url = self.get_absolute_url()
        domain = self.site.domain
        return "http://" + domain + absolute_url

    def save(self, *args, **kwargs):
        """ reset PageMeta and PageTree url cache """
        from pagemeta import PageMeta # against import loops.

        # Clean the local url cache dict
        self._url_cache.clear()
        PageMeta._url_cache.clear()

        # FIXME: We must only update the cache for the current SITE not for all sites.
        try:
            cache.smooth_update() # Save "last change" timestamp in django-tools SmoothCacheBackend
        except AttributeError:
            # No SmoothCacheBackend used -> clean the complete cache
            cache.clear()

        return super(PageTree, self).save(*args, **kwargs)

    def get_site(self):
        """ used e.g. for self.get_absolute_uri() and the admin page """
        return self.site

    def __unicode__(self):
        return u"PageTree %r (id: %i, site: %s, type: %s)" % (
            self.slug, self.id, self.site.domain, self.TYPE_DICT.get(self.page_type)
        )

    class Meta:
        app_label = 'pylucid'
        verbose_name_plural = verbose_name = "PageTree"
        unique_together = (("site", "slug", "parent"),)

        # FIXME: It would be great if we can order by get_absolute_url()
#        ordering = ("site", "id", "position")
        ordering = ("-lastupdatetime",)


# Check Meta.unique_together manually
model_utils.auto_add_check_unique_together(PageTree)

post_save.connect(update_plugin_urls, sender=PageTree)
post_delete.connect(update_plugin_urls, sender=PageTree)
