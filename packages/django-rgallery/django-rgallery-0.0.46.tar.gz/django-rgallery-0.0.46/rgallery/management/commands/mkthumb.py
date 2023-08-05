#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    Tool that regenerate the image cache for all the photos:

    ./manage.py mkthumb

    To run this script from a crontab task we should do something like this:

    */30 * * * * cd /path/to/rgallery-project/ ; source env/bin/activate ; \
                 cd src ; python manage.py mkthumb > /dev/null

    """

    def handle(self, *app_labels, **options):
        """
        The command itself
        """

        print ""
        print "-"*80
        print ""
        print "[***] Making missing thumbs"
        print ""
        thumbs = conf.RGALLLERY_THUMBS
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
