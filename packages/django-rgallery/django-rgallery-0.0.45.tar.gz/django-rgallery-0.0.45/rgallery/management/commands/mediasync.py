#!/usr/bin/env python
# -*- coding: utf-8 -*-

from optparse import make_option
from django.core.management.base import BaseCommand
from django.template import Context, Template
from django.conf import settings as conf
from sorl.thumbnail import get_thumbnail

import rgallery.models as mymodels
from utils import *


# Class MUST be named 'Command'
class Command(BaseCommand):

    # Displayed from 'manage.py help mycommand'
    help = """
    Tool that tries to download and parse photos from a source bucket,
    saving it on the database and converting the photos to fit the web:

    ./manage.py mediasync

    1.- First time it connects with the bucket and if it's Dropbox, stores the
        token information in a token_file
    2.- Next times it read the token from file to connect (only Dropbox)
    3.- Go to the shared folder and check if the image is already on database
    4.- If not, this script download the image, converting it to fit the web and
        save a record in the database.

    To run this script from a crontab task we should do something like this:

    */30 * * * * cd /path/to/rgallery-project/ ; source env/bin/activate ; \
                 cd src ; python manage.py mediasync > /dev/null

    Options:
        --storage=[dropbox|file]
        --source=/path/to/photos (only when storage=file)
        --tags=peques,tag2,tag3

    """

    # If there is a HOMETAG, set is as the default tag importing photos
    try:
        default_tag = conf.HOMETAG
    except:
        default_tag = None

    option_list = BaseCommand.option_list + (
        make_option(
            '--storage',
            dest='storage',
            default='dropbox',
            help='Backend storage where the photos are'
        ),
        make_option(
            '--source',
            dest='source',
            default='/Users/oscar/Desktop/Peques/',
            help='Where the photos are in --storage=file'
        ),
        make_option(
            '--tags',
            dest='tags',
            default=default_tag,
            help='Tag(s) to add to photos --tag=tag1,tag2,tag3'
        ),
    )

    def handle(self, *app_labels, **options):
        """
        The command itself
        """

        # Vars and folders
        storage = options['storage']
        source = options['source']
        try:
            tags = [x.strip() for x in options['tags'].split(',')]
        except:
            tags = ''
        img_duped = 0
        vid_duped = 0
        img_total = 0
        vid_total = 0
        total = 0
        thumbs = conf.RGALLLERY_THUMBS

        # print "*"*80
        # print tags
        # print len(tags)
        # print "*"*80
        # exit(0)

        # Handle connection with the backend (dinamically importing backend)
        # backend_file, backend_dropbox...
        backend = __import__(
            'rgallery.management.commands.backend_%s' % storage,
            fromlist='*')

        print "-"*80
        if options['tags']:
                print "[WWW] Photos are being imported with [%s] tags..." % \
                    options['tags']
        print "[***] Importing..."
        print ""

        # Set dirs (src, dest)
        srcdir, photodestdir, videodestdir = backend.set_dirs(source)

        # Handle connection with the backend
        client, bucket = backend.get_contents(srcdir)

        for file in bucket:
            img_duped, img_total, vid_duped, vid_total, total = mediasync(
                file,
                srcdir,
                photodestdir,
                videodestdir,
                thumbs,
                backend,
                client,
                img_duped,
                vid_duped,
                img_total,
                vid_total,
                total,
                tags)

        print ""
        print "-"*80
        print ""
        print "[***] Making missing thumbs"
        print ""
        conf.THUMBNAIL_DEBUG = True
        allphotos = mymodels.Photo.objects.all()
        for i, p in enumerate(allphotos):
            print "%04d - %s" % (i, p)
            for thumb in thumbs:
                c = Context({'image': p, 'thumb': "%sx%s" % (thumb, thumb)})
                t = Template('{% load thumbnail %}{% thumbnail image thumb crop="top" as img %}{{ img.url }}{% endthumbnail %}')
                t.render(c)
                get_thumbnail(p, "%sx%s" % (thumb, thumb))

        print ""
        print "-"*80
        print ""
        print "[***] Resume images"
        print ""
        print "[***] Duped images (ddbb): %s" % img_duped
        print "[***] Total images: %s" % img_total
        print ""
        print "[***] Resume videos"
        print ""
        print "[***] Duped videos (ddbb): %s" % vid_duped
        print "[***] Total videos: %s" % vid_total
        print ""
        print "[***] TOTAL: %s" % total
        print ""
        print "-"*80
