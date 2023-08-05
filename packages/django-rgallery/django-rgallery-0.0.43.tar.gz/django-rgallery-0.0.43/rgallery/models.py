# -*- coding: utf-8 -*-

"""
Models for the "rgallery" project
"""

import os
import time
import socket
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.template.defaultfilters import slugify
from django.conf import settings as conf

from taggit.managers import TaggableManager


class Folder(models.Model):

    """
    Modelo that defines a folder.
    """

    title = models.CharField(_(u'Title'), max_length=255)
    slug = models.SlugField(_(u'Slug'), max_length=255, unique=True)
    password = models.CharField(_(u'Password'), max_length=255, blank=True,
                                null=True, default='')
    status =  models.BooleanField(_(u'Status'), default=True)

    def __unicode__(self):
        return str(self.title)

    class Meta:
        verbose_name = _(u'Folder')
        verbose_name_plural = _(u'Folders')


class Photo(models.Model):

    """
    Modelo that defines a foto.
    """

    title = models.CharField(_(u'Title'), max_length=255, blank=True, null=True)
    image = models.ImageField(_(u'Image'),
                              upload_to='uploads/photos/', blank=True)
    video = models.FileField(_(u'Video'),
                             upload_to='uploads/videos/', blank=True, null=True)
    origen = models.CharField(_(u'Source file'), max_length=255)
    insert_date = models.DateTimeField(_(u'Insert date'))
    capture_date = models.DateTimeField(_(u'Photo date'))
    folder = models.ForeignKey(Folder, related_name='photo', null=True,
                               blank=True, verbose_name=_(u'Folder'))
    tags = TaggableManager(blank=True)
    status =  models.BooleanField(_(u'Status'), default=True)

    def __unicode__(self):
        return "%s" % str(self.image)

    def split_tags(self):
        t = []
        for tag in self.tags.all():
            t.append(tag.name)
        comma = str(", ".join(t))
        return comma

    def filename(self):
        return os.path.basename(self.image.name)

    def delete(self, *args, **kwargs):
        storage, path = self.image.storage, self.image.path
        if self.video:
            vidstorage, vidpath = self.video.storage, self.video.path
        super(Photo, self).delete(*args, **kwargs)
        storage.delete(path)
        if self.video:
            storage.delete(vidpath)

    class Meta:
        verbose_name = _(u'Photo')
        verbose_name_plural = _(u'Photos')


class Video(models.Model):

    """
    Modelo that defines a video.
    """

    title = models.CharField(_(u'Title'), max_length=255)
    image = models.ImageField(_(u'Video capture'),
                              upload_to='uploads/photos_videos/', blank=True)
    video = models.FileField(_(u'Video'),
                             upload_to='uploads/videos/', blank=True, null=True)
    origen = models.CharField(_(u'Source file'), max_length=255)
    insert_date = models.DateTimeField(_(u'Insert date'))
    capture_date = models.DateTimeField(_(u'Video date'))
    folder = models.ForeignKey(Folder, related_name='video', null=True,
                               blank=True, verbose_name=_(u'Folder'))
    status =  models.BooleanField(_(u'Status'), default=True)

    def __unicode__(self):
        return str(self.title)

    class Meta:
        verbose_name = _('Video')
        verbose_name_plural = _('Videos')
