# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Report'
        db.create_table(u'ImportHub_report', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('total', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
            ('success', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
            ('failed', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
            ('friend', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
            ('incomplete', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, null=True, blank=True)),
            ('pub_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mod_date', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'ImportHub', ['Report'])


    def backwards(self, orm):
        # Deleting model 'Report'
        db.delete_table(u'ImportHub_report')


    models = {
        u'ImportHub.report': {
            'Meta': {'ordering': "['-pub_date']", 'object_name': 'Report'},
            'failed': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'friend': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'incomplete': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'mod_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'pub_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'success': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'total': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['ImportHub']