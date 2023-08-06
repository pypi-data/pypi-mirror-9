# -*- coding: utf-8 -*-
"""
Admin pages for coop_cms
"""

from django.conf import settings
from django.contrib import admin
from django.utils.importlib import import_module
from django.utils.translation import ugettext_lazy as _

from coop_cms.forms import NavTypeForm, ArticleAdminForm, NewsletterItemAdminForm, NewsletterAdminForm
from coop_cms import models
from coop_cms.settings import get_article_class, get_navtree_class

#The BASE_ADMIN_CLASS can be a Translation admin if needed or regular modelAdmin if not
if 'modeltranslation' in settings.INSTALLED_APPS:
    BASE_ADMIN_CLASS = import_module('modeltranslation.admin').TranslationAdmin
else:
    BASE_ADMIN_CLASS = admin.ModelAdmin


def clear_thumbnails_action(model_admin, request, queryset):
    """This action is used by Image Admin and cause sorl-thumbnails to be reset"""
    for obj in queryset:
        obj.clear_thumbnails()
clear_thumbnails_action.short_description = _(u"Clear thumbnails")


class NavNodeAdmin(admin.ModelAdmin):
    """Navigation node admin"""
    list_display = ["label", 'parent', 'ordering', 'in_navigation', 'content_type', 'object_id']

admin.site.register(models.NavNode, NavNodeAdmin)


class NavTypeAdmin(admin.ModelAdmin):
    """Navigation type admin"""
    form = NavTypeForm

admin.site.register(models.NavType, NavTypeAdmin)


class NavTreeAdmin(admin.ModelAdmin):
    """Navigation tree admin"""
    list_display = ['__unicode__', 'name', 'navtypes_list']
    list_editable = ['name']
    list_filters = ['id']

    def nodes_li(self, tree):
        """display the tree nodes for jstree"""
        root_nodes = tree.get_root_nodes()
        nodes_li = u''.join([node.as_jstree() for node in root_nodes])
        return nodes_li

    def navtypes_list(self, tree):
        """list of navigable types"""
        if tree.types.count() == 0:
            return _(u'All')
        else:
            return u' - '.join([unicode(x) for x in tree.types.all()])
    navtypes_list.short_description = _(u'navigable types')

    def change_view(self, request, object_id, extra_context=None, *args, **kwargs):
        """override the change view"""
        extra_context = extra_context or {}
        tree = models.get_navtree_class().objects.get(id=object_id)
        extra_context['navtree'] = tree
        extra_context['navtree_nodes'] = self.nodes_li(tree)
        return super(NavTreeAdmin, self).change_view(
            request, object_id, extra_context=extra_context, *args, **kwargs
        ) # pylint: disable=E1002

admin.site.register(get_navtree_class(), NavTreeAdmin)


class ArticleAdmin(BASE_ADMIN_CLASS):
    """Article admin"""
    form = ArticleAdminForm
    list_display = [
        'slug', 'title', 'category', 'template_name', 'publication', 'headline', 'in_newsletter', 'modified'
    ]
    list_editable = ['publication', 'headline', 'in_newsletter', 'category']
    readonly_fields = ['created', 'modified', 'is_homepage']
    list_filter = ['publication', 'headline', 'in_newsletter', 'sites', 'homepage_for_site', 'category', 'template']
    date_hierarchy = 'publication_date'
    fieldsets = (
        #(_('Navigation'), {'fields': ('navigation_parent',)}),
        (_(u'General'), {'fields': ('slug', 'title', 'subtitle', 'publication', )}),
        (_(u'Settings'), {
            'fields': ('sites', 'template', 'category', 'headline', 'is_homepage', 'logo', 'in_newsletter', )
        }),
        (_(u'Advanced'), {'fields': ('publication_date', 'homepage_for_site', 'created', 'modified', )}),
        (_(u'Content'), {'fields': ('content', 'summary', )}),
        (_(u'Debug'), {'fields': ('temp_logo', )}),
    )

    def get_form(self, request, obj=None, **kwargs):
        """return custom form: It adds the current user"""
        form = super(ArticleAdmin, self).get_form(request, obj, **kwargs) # pylint: disable=E1002
        form.current_user = request.user
        return form

admin.site.register(get_article_class(), ArticleAdmin)


class MediaFilterFilter(admin.SimpleListFilter):
    """filter by media_filter"""
    title = _(u'Media filter')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'media_filter'

    def lookups(self, request, model_admin):
        """values of the filters"""
        media_filters = models.MediaFilter.objects.all()
        return [(x.id, x.name) for x in media_filters]

    def queryset(self, request, queryset):
        """return values after taken the filter into account"""
        value = self.value()
        if value == None:
            return queryset
        return queryset.filter(filters__id=value)


class ImageAdmin(admin.ModelAdmin):
    """Image admin"""
    list_display = ['admin_image', 'name', 'file', 'size', 'ordering']
    list_filter = [MediaFilterFilter, 'size']
    list_editable = ('ordering',)
    search_fields = ['name']
    actions = [clear_thumbnails_action]

admin.site.register(models.Image, ImageAdmin)


class FragmentAdmin(BASE_ADMIN_CLASS):
    """Fragment admin"""
    list_display = ['name', 'position', 'type', 'filter', 'css_class']
    list_filter = ['type', 'filter', 'css_class']

admin.site.register(models.Fragment, FragmentAdmin)


class ArticleCategoryAdmin(admin.ModelAdmin):
    """Article category Admin"""
    list_display = ['name', 'ordering', 'in_rss']
    list_editable = ['ordering', 'in_rss']

admin.site.register(models.ArticleCategory, ArticleCategoryAdmin)


class NewsletterItemAdmin(admin.ModelAdmin):
    """newsletter item Admin"""
    form = NewsletterItemAdminForm
    list_display = ['content_type', 'content_object', 'ordering']
    list_editable = ['ordering']
    fieldsets = (
        (_('Article'), {'fields': ('object_id', 'content_type', 'ordering')}),
    )

admin.site.register(models.NewsletterItem, NewsletterItemAdmin)


class NewsletterAdmin(admin.ModelAdmin):
    """Newsletter Admin"""

    form = NewsletterAdminForm
    raw_id_fields = ['items']
    list_display = ['subject', 'template', 'source_url']

    def get_form(self, request, obj=None, **kwargs):
        """return custom form: it adds the current user"""
        form = super(NewsletterAdmin, self).get_form(request, obj, **kwargs) # pylint: disable=E1002
        form.current_user = request.user
        return form

admin.site.register(models.Newsletter, NewsletterAdmin)


class AliasAdmin(BASE_ADMIN_CLASS):
    """Alias admin"""
    list_display = ['path', 'redirect_url']
    list_editable = ['redirect_url']
admin.site.register(models.Alias, AliasAdmin)

admin.site.register(models.MediaFilter)


class ImageSizeAdmin(admin.ModelAdmin):
    """Image size admin"""
    list_display = ['name', 'size', 'crop']

admin.site.register(models.ImageSize, ImageSizeAdmin)


admin.site.register(models.PieceOfHtml)
admin.site.register(models.NewsletterSending)
admin.site.register(models.FragmentType)
admin.site.register(models.FragmentFilter)
admin.site.register(models.Link)
admin.site.register(models.Document)

admin.site.register(models.SiteSettings, BASE_ADMIN_CLASS)
