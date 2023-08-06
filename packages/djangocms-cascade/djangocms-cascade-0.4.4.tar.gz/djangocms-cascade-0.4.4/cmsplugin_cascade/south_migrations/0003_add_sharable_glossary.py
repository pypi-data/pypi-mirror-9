# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SharedGlossary'
        db.create_table(u'cmsplugin_cascade_sharedglossary', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plugin_type', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('glossary', self.gf('jsonfield.fields.JSONField')(default={}, null=True, blank=True)),
        ))
        db.send_create_signal(u'cmsplugin_cascade', ['SharedGlossary'])

        # Adding unique constraint on 'SharedGlossary', fields ['plugin_type', 'identifier']
        db.create_unique(u'cmsplugin_cascade_sharedglossary', ['plugin_type', 'identifier'])

        # Adding model 'SharableCascadeElement'
        db.create_table(u'cmsplugin_cascade_sharablecascadeelement', (
            ('cmsplugin_ptr', self.gf('django.db.models.fields.related.OneToOneField')(related_name=u'+', unique=True, primary_key=True, to=orm['cms.CMSPlugin'])),
            ('glossary', self.gf('jsonfield.fields.JSONField')(default={}, null=True, blank=True)),
            ('shared_glossary', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cmsplugin_cascade.SharedGlossary'], null=True, on_delete=models.SET_NULL, blank=True)),
        ))
        db.send_create_signal(u'cmsplugin_cascade', ['SharableCascadeElement'])


    def backwards(self, orm):
        # Removing unique constraint on 'SharedGlossary', fields ['plugin_type', 'identifier']
        db.delete_unique(u'cmsplugin_cascade_sharedglossary', ['plugin_type', 'identifier'])

        # Deleting model 'SharedGlossary'
        db.delete_table(u'cmsplugin_cascade_sharedglossary')

        # Deleting model 'SharableCascadeElement'
        db.delete_table(u'cmsplugin_cascade_sharablecascadeelement')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        'cmsplugin_cascade.cascadeelement': {
            'Meta': {'object_name': 'CascadeElement'},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'+'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['cms.CMSPlugin']"}),
            'glossary': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'})
        },
        u'cmsplugin_cascade.sharablecascadeelement': {
            'Meta': {'object_name': 'SharableCascadeElement'},
            'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "u'+'", 'unique': 'True', 'primary_key': 'True', 'to': "orm['cms.CMSPlugin']"}),
            'glossary': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'}),
            'shared_glossary': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['cmsplugin_cascade.SharedGlossary']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        u'cmsplugin_cascade.sharedglossary': {
            'Meta': {'unique_together': "((u'plugin_type', u'identifier'),)", 'object_name': 'SharedGlossary'},
            'glossary': ('jsonfield.fields.JSONField', [], {'default': '{}', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        }
    }

    complete_apps = ['cmsplugin_cascade']