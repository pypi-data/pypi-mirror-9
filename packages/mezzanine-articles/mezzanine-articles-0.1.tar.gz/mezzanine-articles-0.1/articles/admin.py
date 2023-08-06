# -*- coding: UTF-8 -*-
from copy import deepcopy
from django import forms
from django.contrib import admin
from django.db import models
from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin

from .models import Article, ArticleImage, LinkedPage


class GalleryImageInline(TabularDynamicInlineAdmin):
    #def __init__(self, *args,**kwargs):
    #    super(GalleryImageInline, self).__init__(*args, **kwargs)

    classes = ('collapse-open',)
    model = ArticleImage


class LinkedPageInline(TabularDynamicInlineAdmin):
    #def __init__(self, *args,**kwargs):
    #    super(PagesInline, self).__init__(*args, **kwargs)

    classes = ('collapse-open',)
    model = LinkedPage
    fk_name = "article"

    # define the raw_id_fields
    # raw_id_fields = ('page',)
    # define the autocomplete_lookup_fields
    autocomplete_lookup_fields = {
        'fk': ['page'],
    }


class ArticleAdmin(PageAdmin):
    inlines = (GalleryImageInline, LinkedPageInline,)
    fieldsets = (
        (None, {"fields": (
            "title", "status", "cover", "content",
            ('publish_date', 'expiry_date'),
            u'login_required', u'in_menus',)
        }),
        ("meta data", {'fields': (
            '_meta_title', 'slug', (u'description', u'gen_description'),
            u'keywords', u'in_sitemap'),
            'classes': (u'collapse-closed',)},),
        ("sections", {"fields": (
            "sections", "section",),
            "classes": ("grp-collapse", "collapse-closed",)}),
        (None, {"fields": ("zip_import", "show_gallery",)})
    )

    filter_horizontal = ("sections",)

    class Media:
        css = {"all": ("mezzanine/css/admin/gallery.css",)}

    def get_form(self, request, obj=None, **kwargs):
        form = super(ArticleAdmin, self).get_form(request, obj, **kwargs)
        qs = Article.section_list.all()
        if obj and obj.pk:
            qs = qs.exclude(id=obj.id,)
        form.base_fields["sections"].queryset = qs
        return form

    #def save_model(self, request, obj, form, change):
    #    super(AdAdmin, self).save_model(request, obj, form, change)
    #    print form


admin.site.register(Article, ArticleAdmin)
