# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Edito.button_label'
        db.add_column('editos_edito', 'button_label',
                      self.gf('django.db.models.fields.CharField')(default='Go !', max_length=20, blank=True),
                      keep_default=False)

        # Adding field 'Edito.date_created'
        db.add_column('editos_edito', 'date_created',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, default=datetime.datetime(2014, 5, 26, 0, 0), blank=True),
                      keep_default=False)

        # Adding field 'Edito.date_updated'
        db.add_column('editos_edito', 'date_updated',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2014, 5, 26, 0, 0), blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Edito.button_label'
        db.delete_column('editos_edito', 'button_label')

        # Deleting field 'Edito.date_created'
        db.delete_column('editos_edito', 'date_created')

        # Deleting field 'Edito.date_updated'
        db.delete_column('editos_edito', 'date_updated')


    models = {
        'editos.edito': {
            'Meta': {'object_name': 'Edito'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'button_label': ('django.db.models.fields.CharField', [], {'default': "'Go !'", 'max_length': '20', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'display_from': ('django.db.models.fields.DateField', [], {}),
            'display_until': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'text_content': ('django.db.models.fields.CharField', [], {'max_length': '400'}),
            'text_theme': ('django.db.models.fields.CharField', [], {'default': "'light'", 'max_length': '10'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['editos']
