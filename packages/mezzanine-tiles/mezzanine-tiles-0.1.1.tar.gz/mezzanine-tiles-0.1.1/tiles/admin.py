# -*- coding: UTF-8 -*-
from copy import deepcopy
from django import forms
from django.contrib import admin
from django.db import models
from mezzanine.core.admin import TabularDynamicInlineAdmin
from mezzanine.pages.admin import PageAdmin

from .models import Tile, TileSection


class TileAdmin(PageAdmin):
    fieldsets = deepcopy(PageAdmin.fieldsets)
    filter_horizontal = ("sections",)

    def get_form(self, request, obj=None, **kwargs):
        form = super(TileAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["content"].widget = forms.Textarea()
        form.base_fields["in_sitemap"].initial = False
        form.base_fields["in_menus"].initial = []
        return form

    def save_model(self, request, obj, form, change):
        super(TileAdmin, self).save_model(request, obj, form, change)
        # print form


class TileSectionAdmin(PageAdmin):
    fieldsets = deepcopy(PageAdmin.fieldsets)

    def get_form(self, request, obj=None, **kwargs):
        form = super(TileSectionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields["in_sitemap"].initial = False
        form.base_fields["in_menus"].initial = []
        return form

admin.site.register(Tile, TileAdmin)
admin.site.register(TileSection, TileSectionAdmin)