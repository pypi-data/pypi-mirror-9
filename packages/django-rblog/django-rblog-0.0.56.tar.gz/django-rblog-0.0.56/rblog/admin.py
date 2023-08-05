# -*- coding: utf-8 -*-

from django.contrib import admin
from django.conf import settings as conf
from django.core.urlresolvers import reverse

import models as mymodels
import forms as myforms

from engine import expire_view_cache


def make_published(self, request, queryset):
    rows_updated = queryset.update(status=1)
    if rows_updated == 1:
        message_bit = "1 story was"
    else:
        message_bit = "%s stories were" % rows_updated
    self.message_user(
        request,
        "%s successfully marked as published." % message_bit)
make_published.short_description = "Mark selected stories as published"


def make_unpublished(self, request, queryset):
    rows_updated = queryset.update(status=0)
    if rows_updated == 1:
        message_bit = "1 story was"
    else:
        message_bit = "%s stories were" % rows_updated
    self.message_user(
        request,
        "%s successfully marked as unpublished." % message_bit)
make_unpublished.short_description = "Mark selected stories as unpublished"


class PostAdminForm(admin.ModelAdmin):

    list_display = ('title', 'user', 'creation_date', 'ptype',
                    'status', 'temp_view')
    list_filter = ('user', 'creation_date', 'ptype', 'status')
    ordering = ('-creation_date', )
    search_fields = ('title', 'text', )
    actions = [make_published, make_unpublished]
    prepopulated_fields = {'slug': ['title']}
    exclude = ('user',)

    if "rgallery" in conf.INSTALLED_APPS:
        filter_horizontal = ['photo', 'video']

    """
    On Post save we want to save the user that is editing the post [1] and we
    want to regenerate both caches [2] (blog-index and post-detail pages). To
    see how cache and memcache works take a look on engine.expire_view_cache

    1. http://www.b-list.org/weblog/2008/dec/24/admin/
    2. http://stackoverflow.com/questions/2268417/expire-a-view-cache-in-django
    """

    def save_model(self, request, obj, form, change):
        expire_view_cache("app_blog-index")
        expire_view_cache("app_blog-post-detail", [obj.slug])
        if not change:
            obj.user = request.user
        obj.save()

    """
    Adding TinyMCE in newforms-admin:
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor#Withnewforms-admin
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor
    """

    class Media:
        js = ('js/tiny_mce/tiny_mce.js',
              'js/textareas.js',
              )

    def temp_view(self, obj):
        uri = reverse('app_blog-post-detail-temp', args=(obj.slug,))
        return '<a href="%s">%s</a>' % (uri, obj.title)
    temp_view.allow_tags = True

admin.site.register(mymodels.Post, PostAdminForm)
admin.site.register(mymodels.Comments)
