# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'TaskResult'
        db.delete_table(u'grabstat_taskresult')

        # Adding model 'Task'
        db.create_table(u'grabstat_task', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('record_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('stop_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=10, db_index=True, blank=True)),
            ('error_traceback', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('spider_stats', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('spider_timing', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('work_time', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('pid', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('task_name', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
        ))
        db.send_create_signal(u'grabstat', ['Task'])


    def backwards(self, orm):
        # Adding model 'TaskResult'
        db.create_table(u'grabstat_taskresult', (
            ('status', self.gf('django.db.models.fields.CharField')(default='new', max_length=10, blank=True, db_index=True)),
            ('error_traceback', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('spider_timing', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True, db_index=True)),
            ('pid', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('work_time', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('spider_stats', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('stop_time', self.gf('django.db.models.fields.DateTimeField')(blank=True, null=True, db_index=True)),
            ('task_name', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('record_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True, db_index=True)),
        ))
        db.send_create_signal(u'grabstat', ['TaskResult'])

        # Deleting model 'Task'
        db.delete_table(u'grabstat_task')


    models = {
        u'grabstat.task': {
            'Meta': {'object_name': 'Task'},
            'error_traceback': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'record_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'spider_stats': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'spider_timing': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '10', 'db_index': 'True', 'blank': 'True'}),
            'stop_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'task_name': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'work_time': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['grabstat']