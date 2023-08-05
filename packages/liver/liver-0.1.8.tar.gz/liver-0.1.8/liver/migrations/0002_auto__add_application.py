# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Application'
        db.create_table(u'liver_application', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=2500, blank=True)),
            ('token', self.gf('django.db.models.fields.CharField')(max_length=500, blank=True)),
            ('insertion_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, db_index=True, blank=True)),
            ('modification_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, null=True, db_index=True, blank=True)),
            ('valid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('valid_since', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('valid_until', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, db_index=True, blank=True)),
            ('sync_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'liver', ['Application'])


    def backwards(self, orm):
        # Deleting model 'Application'
        db.delete_table(u'liver_application')


    models = {
        u'liver.application': {
            'Meta': {'object_name': 'Application'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2500', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insertion_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'modification_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'sync_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'valid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'valid_since': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'valid_until': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'})
        },
        u'liver.recorder': {
            'Meta': {'object_name': 'Recorder'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'3c2d8374-6ce2-11e4-83cd-8d34ee488137'", 'max_length': '5000'})
        },
        u'liver.recording': {
            'Meta': {'object_name': 'Recording'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insertion_date': ('django.db.models.fields.DateTimeField', [], {}),
            'metadata_json': ('django.db.models.fields.TextField', [], {'max_length': '5000', 'blank': 'True'}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'blank': 'True'}),
            'profiles_json': ('django.db.models.fields.TextField', [], {'max_length': '5000', 'blank': 'True'}),
            'recorder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['liver.Recorder']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'recording_job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['liver.RecordingJob']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'to_delete': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'liver.recordingjob': {
            'Meta': {'object_name': 'RecordingJob'},
            'completion_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'execution_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insertion_date': ('django.db.models.fields.DateTimeField', [], {}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'recorder': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['liver.Recorder']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'recording_source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['liver.RecordingSource']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'result': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '5000', 'null': 'True', 'blank': 'True'}),
            'scheduled_duration': ('django.db.models.fields.IntegerField', [], {}),
            'scheduled_end_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'scheduled_start_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sources_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['liver.SourcesGroup']"}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '5000'})
        },
        u'liver.recordingjobmetadata': {
            'Meta': {'object_name': 'RecordingJobMetadata'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'blank': 'True'}),
            'recording_job': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['liver.RecordingJob']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'blank': 'True'})
        },
        u'liver.recordingmetadata': {
            'Meta': {'object_name': 'RecordingMetadata'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'blank': 'True'}),
            'recording_source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['liver.RecordingSource']"}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'blank': 'True'})
        },
        u'liver.recordingrule': {
            'Meta': {'object_name': 'RecordingRule'},
            'availability_window': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata_key_filter': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'blank': 'True'}),
            'metadata_value_filter': ('django.db.models.fields.CharField', [], {'max_length': '5000', 'blank': 'True'}),
            'offset_end': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'offset_start': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'recording_source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['liver.RecordingSource']"})
        },
        u'liver.recordingsource': {
            'Meta': {'object_name': 'RecordingSource'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'enabled_since': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'enabled_until': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'external_id': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '5000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insertion_date': ('django.db.models.fields.DateTimeField', [], {}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'sources_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['liver.SourcesGroup']", 'null': 'True', 'blank': 'True'})
        },
        u'liver.source': {
            'Meta': {'object_name': 'Source'},
            'bitrate': ('django.db.models.fields.IntegerField', [], {'default': '1000000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insertion_date': ('django.db.models.fields.DateTimeField', [], {}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            'sources_group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['liver.SourcesGroup']", 'null': 'True', 'blank': 'True'}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '5000'})
        },
        u'liver.sourcesgroup': {
            'Meta': {'object_name': 'SourcesGroup'},
            'default_availability_window': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'default_offset_end': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'default_offset_start': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'external_id': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insertion_date': ('django.db.models.fields.DateTimeField', [], {}),
            'modification_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '5000'})
        }
    }

    complete_apps = ['liver']