# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import datetime
import gzip
import glob

from django.conf import settings as conf
from dropbox import client, rest, session

from utils import *


def set_dirs(source):
    source = os.path.join(conf.PROJECT_DIR, 'media', 'uploads', 'dropbox')
    photo_target = os.path.join(conf.PROJECT_DIR, 'media', 'uploads', 'photos')
    video_target = os.path.join(conf.PROJECT_DIR, 'media', 'uploads', 'videos')
    if os.path.exists(photo_target) == False:
        mkdir_p(photo_target)
    if os.path.exists(video_target) == False:
        mkdir_p(video_target)
    return source, photo_target, video_target


def get_contents(srcdir):
    """
    Handle Dropbox connection
    """
    # Get your app key and secret from the Dropbox developer website
    APP_KEY = conf.DROPBOX_APP_KEY
    APP_SECRET = conf.DROPBOX_APP_SECRET

    # ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
    try:
        ACCESS_TYPE = conf.DROPBOX_ACCESS_TYPE
    except:
        ACCESS_TYPE = 'dropbox'

    # Creating dirs
    if os.path.exists(srcdir) == False:
        mkdir_p(srcdir)

    # First time
    TOKENS = os.path.join(conf.PROJECT_DIR, 'media', 'uploads', 'dropbox', 'dropbox_token.txt')
    if not os.path.exists(TOKENS):
        sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)
        request_token = sess.obtain_request_token()
        url = sess.build_authorize_url(request_token)

        # Make the user sign in and authorize this token
        print "url:", url
        print "Please visit this website and press the 'Allow' button, then hit 'Enter' here."
        raw_input()

        # This will fail if the user didn't visit the above URL
        access_token = sess.obtain_access_token(request_token)

        token_file = open(TOKENS,'w')
        token_file.write("%s|%s" % (access_token.key,access_token.secret) )
        token_file.close()
    else:
        token_file = open(TOKENS)
        token_key,token_secret = token_file.read().split('|')
        token_file.close()
        sess = session.DropboxSession(APP_KEY,APP_SECRET, ACCESS_TYPE )
        sess.set_token(token_key,token_secret)

    c = client.DropboxClient(sess)

    #if debug:
    #    print "linked account:", c.account_info()

    # DROPBOX_PATH: If the access is 'dropbox' you have to specify the folder
    # If it's 'app_folder' it's ok with /
    try:
        DROPBOX_PATH = conf.DROPBOX_ACCESS_PATH
    except:
        DROPBOX_PATH = '/'

    folder_metadata = c.metadata(DROPBOX_PATH)
    #if debug:
    #    print "*"*80
    #    print "metadata:", folder_metadata
    #    print "*"*80
    #    print "contents:", folder_metadata['contents']
    #    print "-"*80

    #if debug:
    #    for file in folder_metadata['contents']:
    #        print file

    return c, folder_metadata['contents']


def filepath(file):
    return file['path']


def is_image(cont):
    try:
        str(cont['mime_type'])
    except:
        cont['mime_type'] = ''

    if cont['mime_type'] == 'image/jpeg':
        return True
    return False


def is_video(cont):
    try:
        str(cont['mime_type'])
    except:
        cont['mime_type'] = ''

    if cont['mime_type'] == 'video/mp4' or cont['mime_type'] == 'video/3gpp':
        return True
    return False


def download(client, file, nombre_imagen, srcdir, destdir):
    f, metadata = client.get_file_and_metadata(file['path'])
    img = os.path.join(srcdir, nombre_imagen)
    out = open(img, 'wb')
    out.write(f.read())
    out.close()
    return img
