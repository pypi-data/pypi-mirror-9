# -*- coding: utf-8 -*-

import os.path
from django.contrib import admin
from django.utils.safestring import mark_safe

import models as mymodels
import forms as myforms
import socket

from engine import expire_view_cache
from sorl.thumbnail import get_thumbnail


class FolderAdminForm(admin.ModelAdmin):
    prepopulated_fields = {'slug': ['title']}


class PhotoAdminForm(admin.ModelAdmin):
    list_display = ('thumb', 'image', 'folder', 'capture_date')
    search_fields = ('image', 'origen', )
    ordering = ('-capture_date', )

    def thumb(self, obj):
        try:
            if obj.image:
                tb = get_thumbnail(obj.image, "60x60")
                return mark_safe('<img width="%s" src="%s" />') % (tb.width, tb.url)
            else:
                return "No image"
        except:
            return "No Image"

    thumb.short_description = 'Photo Thumb'
    thumb.allow_tags = True

    def save_model(self, request, obj, form, change):
        expire_view_cache("app_gallery-gallery")
        folders = mymodels.Folder.objects.all()
        if folders is not None:
            for f in folders:
                expire_view_cache("app_gallery-folder", [f.slug])
        obj.save()

class VideoAdminForm(admin.ModelAdmin):
    list_display = ('thumb', 'video', 'image', 'capture_date')
    search_fields = ('video', 'image', 'origen', )
    ordering = ('-capture_date', )

    def thumb(self, obj):
        try:
            if obj.image:
                tb = get_thumbnail(obj.image, "60x60")
                return mark_safe('<img width="%s" src="%s" />') % (tb.width, tb.url)
            else:
                return "No image"
        except:
            return "No Image"

    thumb.short_description = 'Video Thumb'
    thumb.allow_tags = True

admin.site.register(mymodels.Photo, PhotoAdminForm)
admin.site.register(mymodels.Video, VideoAdminForm)
admin.site.register(mymodels.Folder, FolderAdminForm)
