# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Rule'
        db.delete_table(u'django_diazo_rule')

        # Deleting model 'SingleRule'
        db.delete_table(u'django_diazo_singlerule')

        # Deleting model 'CompoundRule'
        db.delete_table(u'django_diazo_compoundrule')

        # Removing M2M table for field rules on 'CompoundRule'
        db.delete_table(db.shorten_name(u'django_diazo_compoundrule_rules'))

        # Deleting field 'Theme.rules'
        db.delete_column(u'django_diazo_theme', 'rules_id')


    def backwards(self, orm):
        # Adding model 'Rule'
        db.create_table(u'django_diazo_rule', (
            ('polymorphic_ctype', self.gf('django.db.models.fields.related.ForeignKey')(related_name='polymorphic_django_diazo.rule_set', null=True, to=orm['contenttypes.ContentType'])),
            ('root', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('django_diazo', ['Rule'])

        # Adding model 'SingleRule'
        db.create_table(u'django_diazo_singlerule', (
            ('rule_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['django_diazo.Rule'], unique=True, primary_key=True)),
            ('rule', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('django_diazo', ['SingleRule'])

        # Adding model 'CompoundRule'
        db.create_table(u'django_diazo_compoundrule', (
            ('prefix', self.gf('django.db.models.fields.TextField')()),
            ('rule_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['django_diazo.Rule'], unique=True, primary_key=True)),
            ('suffix', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('django_diazo', ['CompoundRule'])

        # Adding M2M table for field rules on 'CompoundRule'
        m2m_table_name = db.shorten_name(u'django_diazo_compoundrule_rules')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('compoundrule', models.ForeignKey(orm['django_diazo.compoundrule'], null=False)),
            ('rule', models.ForeignKey(orm['django_diazo.rule'], null=False))
        ))
        db.create_unique(m2m_table_name, ['compoundrule_id', 'rule_id'])

        # Adding field 'Theme.rules'
        db.add_column(u'django_diazo_theme', 'rules',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='themes', null=True, to=orm['django_diazo.Rule'], blank=True),
                      keep_default=False)


    models = {
        u'django_diazo.theme': {
            'Meta': {'ordering': "('sort',)", 'object_name': 'Theme'},
            'builtin': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'debug': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
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