# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Theme.pattern'
        db.add_column(u'django_diazo_theme', 'pattern',
                      self.gf('django.db.models.fields.CharField')(default='.*', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Theme.pattern'
        db.delete_column(u'django_diazo_theme', 'pattern')


    models = {
        u'django_diazo.theme': {
            'Meta': {'ordering': "('sort',)", 'object_name': 'Theme'},
            'builtin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'debug': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pattern': ('django.db.models.fields.CharField', [], {'default': "'.*'", 'max_length': '255'}),
            'prefix': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        u'django_diazo.themeuseragent': {
            'Meta': {'object_name': 'ThemeUserAgent'},
            'allow': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sort': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'theme': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'useragent_strings'", 'to': u"orm['django_diazo.Theme']"})
        }
    }

    complete_apps = ['django_diazo']