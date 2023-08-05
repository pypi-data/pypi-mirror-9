# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SourcesGroup'
        db.create_table(u'liver_sourcesgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=5000)),
            ('external_id', self.gf('django.db.models.fields.CharField')(max_length=5000)),
            ('insertion_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, null=True, blank=True)),
            ('default_offset_start', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('default_offset_end', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('default_availability_window', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'liver', ['SourcesGroup'])

        # Adding model 'Source'
        db.create_table(u'liver_source', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=5000)),
            ('uri', self.gf('django.db.models.fields.CharField')(max_length=5000)),
            ('bitrate', self.gf('django.db.models.fields.IntegerField')(default=1000000)),
            ('insertion_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, null=True, blank=True)),
            ('sources_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['liver.SourcesGroup'], null=True, blank=True)),
        ))
        db.send_create_signal(u'liver', ['Source'])

        # Adding model 'Recorder'
        db.create_table(u'liver_recorder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=5000)),
            ('token', self.gf('django.db.models.fields.CharField')(default='674bc67c-6429-11e4-83cd-61e6ff356173', max_length=5000)),
        ))
        db.send_create_signal(u'liver', ['Recorder'])

        # Adding model 'RecordingSource'
        db.create_table(u'liver_recordingsource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('external_id', self.gf('django.db.models.fields.CharField')(default='', max_length=5000)),
            ('sources_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['liver.SourcesGroup'], null=True, blank=True)),
            ('insertion_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('enabled_since', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('enabled_until', self.gf('django.db.models.fields.DateTimeField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal(u'liver', ['RecordingSource'])

        # Adding model 'RecordingMetadata'
        db.create_table(u'liver_recordingmetadata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['liver.RecordingSource'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=5000, blank=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=5000, blank=True)),
        ))
        db.send_create_signal(u'liver', ['RecordingMetadata'])

        # Adding model 'RecordingRule'
        db.create_table(u'liver_recordingrule', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['liver.RecordingSource'])),
            ('metadata_key_filter', self.gf('django.db.models.fields.CharField')(max_length=5000, blank=True)),
            ('metadata_value_filter', self.gf('django.db.models.fields.CharField')(max_length=5000, blank=True)),
            ('offset_start', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('offset_end', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('availability_window', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'liver', ['RecordingRule'])

        # Adding model 'RecordingJob'
        db.create_table(u'liver_recordingjob', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['liver.RecordingSource'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('sources_group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['liver.SourcesGroup'])),
            ('insertion_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, null=True, blank=True)),
            ('execution_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('completion_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('scheduled_start_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('scheduled_end_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('scheduled_duration', self.gf('django.db.models.fields.IntegerField')()),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('recorder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['liver.Recorder'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('result', self.gf('django.db.models.fields.CharField')(default='None', max_length=5000, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=5000)),
        ))
        db.send_create_signal(u'liver', ['RecordingJob'])

        # Adding model 'RecordingJobMetadata'
        db.create_table(u'liver_recordingjobmetadata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording_job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['liver.RecordingJob'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=5000, blank=True)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=5000, blank=True)),
        ))
        db.send_create_signal(u'liver', ['RecordingJobMetadata'])

        # Adding model 'Recording'
        db.create_table(u'liver_recording', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('recording_job', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['liver.RecordingJob'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('recorder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['liver.Recorder'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=5000, blank=True)),
            ('insertion_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('modification_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, null=True, blank=True)),
            ('metadata_json', self.gf('django.db.models.fields.TextField')(max_length=5000, blank=True)),
            ('profiles_json', self.gf('django.db.models.fields.TextField')(max_length=5000, blank=True)),
            ('to_delete', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'liver', ['Recording'])


    def backwards(self, orm):
        # Deleting model 'SourcesGroup'
        db.delete_table(u'liver_sourcesgroup')

        # Deleting model 'Source'
        db.delete_table(u'liver_source')

        # Deleting model 'Recorder'
        db.delete_table(u'liver_recorder')

        # Deleting model 'RecordingSource'
        db.delete_table(u'liver_recordingsource')

        # Deleting model 'RecordingMetadata'
        db.delete_table(u'liver_recordingmetadata')

        # Deleting model 'RecordingRule'
        db.delete_table(u'liver_recordingrule')

        # Deleting model 'RecordingJob'
        db.delete_table(u'liver_recordingjob')

        # Deleting model 'RecordingJobMetadata'
        db.delete_table(u'liver_recordingjobmetadata')

        # Deleting model 'Recording'
        db.delete_table(u'liver_recording')


    models = {
        u'liver.recorder': {
            'Meta': {'object_name': 'Recorder'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '5000'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'674bc67c-6429-11e4-83cd-61e6ff356173'", 'max_length': '5000'})
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