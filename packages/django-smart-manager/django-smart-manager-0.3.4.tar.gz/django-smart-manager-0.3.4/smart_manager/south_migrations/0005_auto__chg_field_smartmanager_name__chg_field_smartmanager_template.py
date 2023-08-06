# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'SmartManagerObject', fields ['smart_manager', 'model_obj_type', 'model_obj_id']
        db.delete_unique(u'smart_manager_smartmanagerobject', ['smart_manager_id', 'model_obj_type_id', 'model_obj_id'])


        # Changing field 'SmartManager.name'
        db.alter_column(u'smart_manager_smartmanager', 'name', self.gf('django.db.models.fields.CharField')(max_length=128, unique=True, null=True))
        # Adding unique constraint on 'SmartManagerObject', fields ['model_obj_type', 'model_obj_id']
        db.create_unique(u'smart_manager_smartmanagerobject', ['model_obj_type_id', 'model_obj_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'SmartManagerObject', fields ['model_obj_type', 'model_obj_id']
        db.delete_unique(u'smart_manager_smartmanagerobject', ['model_obj_type_id', 'model_obj_id'])


        # Changing field 'SmartManager.name'
        db.alter_column(u'smart_manager_smartmanager', 'name', self.gf('django.db.models.fields.CharField')(default='', max_length=128, unique=True))
        # Adding unique constraint on 'SmartManagerObject', fields ['smart_manager', 'model_obj_type', 'model_obj_id']
        db.create_unique(u'smart_manager_smartmanagerobject', ['smart_manager_id', 'model_obj_type_id', 'model_obj_id'])


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'smart_manager.smartmanager': {
            'Meta': {'object_name': 'SmartManager'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manages_deletions': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '128', 'unique': 'True', 'null': 'True'}),
            'smart_manager_class': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'template': ('jsonfield.fields.JSONField', [], {})
        },
        u'smart_manager.smartmanagerobject': {
            'Meta': {'unique_together': "(('model_obj_type', 'model_obj_id'),)", 'object_name': 'SmartManagerObject'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_obj_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'model_obj_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'smart_manager': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['smart_manager.SmartManager']"})
        }
    }

    complete_apps = ['smart_manager']