# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import datetime
import gzip
import glob
from mimetypes import MimeTypes

from django.conf import settings as conf

from utils import *


class File(object):
    path = ""
    mime_type = ""

    # The class "constructor" - It's actually an initializer
    def __init__(self, path):
        self.path = path
        try:
            mime = MimeTypes()
            m = str(mime.guess_type(self.path)[0])
        except:
            m = ''
        self.mime_type = m


def set_dirs(source):
    source = source
    photo_target = os.path.join(conf.PROJECT_DIR, 'media', 'uploads', 'photos')
    video_target = os.path.join(conf.PROJECT_DIR, 'media', 'uploads', 'videos')
    if os.path.exists(photo_target) == False:
        mkdir_p(photo_target)
    if os.path.exists(video_target) == False:
        mkdir_p(video_target)
    return source, photo_target, video_target


def get_contents(srcdir):
    types = (os.path.join(srcdir, '*'),)
    bucket = []
    for files in types:
        bucket.extend(glob.glob(files))

    file2 = []
    for file in bucket:
        file2.append(File(file))

    # Returns False for compatibility reasons
    return False, file2


def filepath(file):
    return file.path


def is_image(file):
    if file.mime_type == 'image/jpeg':
        return True
    return False


def is_video(file):
    if file.mime_type == 'video/mp4' or file.mime_type == 'video/3gpp' or file.mime_type == 'video/quicktime' or file.mime_type == 'video/x-msvideo':
        return True
    return False


def download(client, file, nombre_imagen, srcdir, destdir):
    # Keeps client and destdir arguments for compatibility reasons
    # but they're  not used
    f = open(file.path, 'r')
    img = os.path.join(destdir, nombre_imagen)
    out = open(img, 'wb')
    out.write(f.read())
    out.close()
    return img
