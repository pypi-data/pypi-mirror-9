# -*- coding: utf-8 -*-

import os
import json
import zipfile
import urllib2
from StringIO import StringIO

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
import models as mymodels

from braces.views import LoginRequiredMixin, SuperuserRequiredMixin
from taggit.models import Tag

from django.conf import settings as conf

from django.views.generic import ListView, CreateView

from engine import expire_view_cache
from management.commands.utils import *
from forms import PhotoForm


class TagMixin(object):
    def get_context_data(self, **kwargs):
        context = super(TagMixin, self).get_context_data(**kwargs)
        if self.request.user.is_superuser:
            context['tags'] = Tag.objects.all()
        else:
            tags = Tag.objects.filter(photo__status=True)
            context['tags'] = tags.distinct()
        return context


class Photos(TagMixin, ListView):

    template_name = "rgallery/photos.html"
    context_object_name = "photos"
    paginate_by = 150

    def get_queryset(self):
        if self.request.user.is_superuser:
            return mymodels.Photo.objects.all().order_by('-capture_date')
        else:
            try:
                return mymodels.Photo.objects.all().filter(
                    status=1,
                    folder__isnull=True,
                    tags__slug=conf.HOMETAG).order_by('-capture_date')
            except:
                return mymodels.Photo.objects.all().filter(
                    status=1,
                    folder__isnull=True).order_by('-capture_date')

    def get_context_data(self, **kwargs):
        context = super(Photos, self).get_context_data(**kwargs)
        folders = mymodels.Folder.objects.filter(status=1)
        form = PhotoForm

        context.update({
            'title': _(u'Photos'),
            'form': form,
            'folders': folders,
        })
        return context


class PhotosFolder(ListView):

    template_name = "rgallery/photos.html"
    context_object_name = "photos"

    def get_queryset(self):
        folder = mymodels.Folder.objects.get(slug=self.kwargs['folder'])
        return mymodels.Photo.objects.all().filter(
            status=1,
            folder=folder).order_by('-capture_date')

    def get_context_data(self, **kwargs):
        context = super(PhotosFolder, self).get_context_data(**kwargs)

        context.update({
            'title': _(u'Photos'),
        })
        return context


class PhotosTag(ListView):

    template_name = "rgallery/photos.html"
    model = mymodels.Photo
    context_object_name = "photos"
    paginate_by = 150

    def get_queryset(self):
        if self.request.user.is_superuser:
            return mymodels.Photo.objects.filter(
                tags__slug=self.kwargs.get(
                    'slug', None)).order_by('-capture_date')
        else:
            return mymodels.Photo.objects.filter(
                status=1,
                tags__slug=self.kwargs.get(
                    'slug', None)).order_by('-capture_date')

    def get_context_data(self, **kwargs):
        context = super(PhotosTag, self).get_context_data(**kwargs)

        context.update({
            'tag': self.kwargs.get('slug', None),
        })
        return context


class PhotoAddTag(LoginRequiredMixin, SuperuserRequiredMixin, ListView):

    model = mymodels.Photo

    def post(self, request, *args, **kwargs):
        if self.request.is_ajax() and self.request.method == 'POST':
            pk = json.loads(self.request.POST.get('pk', None))
            tags = json.loads(self.request.POST.get('tags', None))
            response_data = {}
            if type(pk) is list:
                # List
                photos = mymodels.Photo.objects.filter(id__in=pk)
                for photo in photos:
                    photo.tags.clear()
                    if len(tags) > 0:
                        for tag in tags:
                            try:
                                t = Tag.objects.get(slug=tag)
                                photo.tags.add(t)
                            except:
                                photo.tags.add(tag)
                    photo.save()
                    key = 'html-%s' % photo.pk
                    response_data[key] = render_to_string(
                        'rgallery/_listags.html',
                        {'record': photo.tags.all()})
                response_data['multiple'] = 1
                response_data['pk'] = pk
            else:
                # Id
                photo = get_object_or_404(mymodels.Photo, pk=pk)
                photo.tags.clear()
                if len(tags) > 0:
                    for tag in tags:
                        try:
                            t = Tag.objects.get(slug=tag)
                            photo.tags.add(t)
                        except:
                            photo.tags.add(tag)
                photo.save()
                response_data['multiple'] = 0
                response_data['html'] = render_to_string(
                    'rgallery/_listags.html',
                    {'record': photo.tags.all()})
            expire_view_cache("app_gallery-gallery")
            return HttpResponse(json.dumps(response_data),
                                content_type="application/json")


class PhotoAdd(LoginRequiredMixin, SuperuserRequiredMixin, CreateView):

    model = mymodels.Photo
    form_class = PhotoForm
    success_url = '/'

    def form_valid(self, form):
        self.object = form.save(commit=False)

        backend = __import__('rgallery.management.commands.backend_form',
                             fromlist='*')

        # Set dirs (src, dest)
        srcdir, photodestdir, videodestdir = backend.set_dirs(
            form.files['file'])

        img_duped, img_total, vid_duped, vid_total, total = mediasync(
            form.files['file'],
            srcdir,
            photodestdir,
            videodestdir,
            conf.RGALLLERY_THUMBS,
            backend,
            False,
            0,
            0,
            0,
            0,
            0,
            '')

        expire_view_cache("app_gallery-gallery")
        return HttpResponseRedirect(self.get_success_url())


class PhotoDelete(LoginRequiredMixin, SuperuserRequiredMixin, ListView):

    model = mymodels.Photo
    template_name = "rgallery/photo_delete.html"

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax() and self.request.method == 'GET':
            pk = json.loads(self.request.GET.get('pk', None))
            response_data = {}
            if type(pk) is list:
                # List
                photos = mymodels.Photo.objects.filter(id__in=pk)
                for photo in photos:
                    photo.delete()
                response_data['pk'] = pk
                response_data['multiple'] = 1
            else:
                # Id
                photo = get_object_or_404(mymodels.Photo, pk=pk)
                photo.delete()
                response_data['pk'] = pk
                response_data['multiple'] = 0
            expire_view_cache("app_gallery-gallery")
            return HttpResponse(json.dumps(response_data),
                                content_type="application/json")


class PhotoDownload(LoginRequiredMixin, ListView):

    model = mymodels.Photo
    template_name = "rgallery/photo_delete.html"

    def render_to_response(self, context):
        pk = urllib2.unquote(self.request.COOKIES.get("selected", None))
        pk = filter(None, pk.split(','))
        # List
        s = StringIO()
        zf = zipfile.ZipFile(s, "w")

        photos = mymodels.Photo.objects.filter(id__in=pk)
        for photo in photos:
            fdir, fname = os.path.split(photo.image.path)
            zf.write(photo.image.path, fname)
        zf.close()
        resp = HttpResponse(s.getvalue(),
                            mimetype="application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=photos.zip'
        return resp


class PhotoChangeStatus(LoginRequiredMixin, SuperuserRequiredMixin, ListView):

    model = mymodels.Photo
    template_name = "rgallery/photo_delete.html"

    def get(self, request, *args, **kwargs):
        if self.request.is_ajax() and self.request.method == 'GET':
            pk = json.loads(self.request.GET.get('pk', None))
            status = json.loads(self.request.GET.get('status', None))
            response_data = {}
            if type(pk) is list:
                # List
                photos = mymodels.Photo.objects.filter(id__in=pk)
                for photo in photos:
                    photo.status = status
                    photo.save()
                response_data['pk'] = pk
                response_data['status'] = status
                response_data['multiple'] = 1
            else:
                # Id
                photo = get_object_or_404(mymodels.Photo, pk=pk)
                if photo.status == 1:
                    photo.status = 0
                else:
                    photo.status = 1
                photo.save()
                response_data['pk'] = pk
                response_data['status'] = photo.status
                response_data['multiple'] = 0
            expire_view_cache("app_gallery-gallery")
            return HttpResponse(json.dumps(response_data),
                                content_type="application/json")


class PhotoGetVideo(LoginRequiredMixin, ListView):

    model = mymodels.Photo

    def post(self, request, *args, **kwargs):
        if self.request.is_ajax() and self.request.method == 'POST':
            pk = json.loads(self.request.POST.get('pk', None))
            photo = get_object_or_404(mymodels.Photo, pk=pk)
            rendered = render_to_string('rgallery/_video.html',
                                        {'video': photo.video})
        return HttpResponse(rendered)


class Videos(ListView):

    template_name = "rgallery/videos.html"
    context_object_name = "videos"
    paginate_by = 150

    def get_queryset(self):
        vid = mymodels.Video.objects.all().filter(
            status=1, folder__isnull=True).order_by('-capture_date')
        print vid
        return vid

    def get_context_data(self, **kwargs):
        context = super(Videos, self).get_context_data(**kwargs)
        context.update({
            'title': _(u'Videos'),
        })
        return context
