# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Photo.folder'
        db.add_column('rgallery_photo', 'folder',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='photo', null=True, to=orm['rgallery.Folder']),
                      keep_default=False)

        # Adding field 'Video.folder'
        db.add_column('rgallery_video', 'folder',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='video', null=True, to=orm['rgallery.Folder']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Photo.folder'
        db.delete_column('rgallery_photo', 'folder_id')

        # Deleting field 'Video.folder'
        db.delete_column('rgallery_video', 'folder_id')


    models = {
        'rgallery.folder': {
            'Meta': {'object_name': 'Folder'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '255'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'rgallery.photo': {
            'Meta': {'object_name': 'Photo'},
            'capture_date': ('django.db.models.fields.DateTimeField', [], {}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'photo'", 'null': 'True', 'to': "orm['rgallery.Folder']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'insert_date': ('django.db.models.fields.DateTimeField', [], {}),
            'origen': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'rgallery.video': {
            'Meta': {'object_name': 'Video'},
            'capture_date': ('django.db.models.fields.DateTimeField', [], {}),
            'folder': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'video'", 'null': 'True', 'to': "orm['rgallery.Folder']"}),
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