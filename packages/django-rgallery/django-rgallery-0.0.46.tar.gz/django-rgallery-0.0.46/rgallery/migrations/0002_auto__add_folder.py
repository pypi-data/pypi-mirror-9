# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Folder'
        db.create_table('rgallery_folder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=255)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('status', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('rgallery', ['Folder'])


    def backwards(self, orm):
        # Deleting model 'Folder'
        db.delete_table('rgallery_folder')


    models = {
        'rgallery.folder': {
            'Meta': {'object_name': 'Folder'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'rgallery.photo': {
            'Meta': {'object_name': 'Photo'},
            'capture_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'insert_date': ('django.db.models.fields.DateTimeField', [], {}),
            'origen': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'rgallery.video': {
            'Meta': {'object_name': 'Video'},
            'capture_date': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'insert_date': ('django.db.models.fields.DateTimeField', [], {}),
            'origen': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'video': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['rgallery']