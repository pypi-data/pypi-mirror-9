# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Edito'
        db.create_table('editos_edito', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('image', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('text_content', self.gf('django.db.models.fields.CharField')(max_length=400)),
            ('display_from', self.gf('django.db.models.fields.DateField')()),
            ('display_until', self.gf('django.db.models.fields.DateField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('text_theme', self.gf('django.db.models.fields.CharField')(default='light', max_length=10)),
        ))
        db.send_create_signal('editos', ['Edito'])


    def backwards(self, orm):
        # Deleting model 'Edito'
        db.delete_table('editos_edito')


    models = {
        'editos.edito': {
            'Meta': {'object_name': 'Edito'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
