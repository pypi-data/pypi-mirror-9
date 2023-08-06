# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Resource'
        db.create_table('oembed_resource', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=255, db_index=True)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('html', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'bambu_oembed', ['Resource'])

        # Adding unique constraint on 'Resource', fields ['url', 'width']
        db.create_unique('oembed_resource', ['url', 'width'])


    def backwards(self, orm):
        # Removing unique constraint on 'Resource', fields ['url', 'width']
        db.delete_unique('oembed_resource', ['url', 'width'])

        # Deleting model 'Resource'
        db.delete_table('oembed_resource')


    models = {
        u'bambu_oembed.resource': {
            'Meta': {'unique_together': "(('url', 'width'),)", 'object_name': 'Resource', 'db_table': "'oembed_resource'"},
            'html': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'db_index': 'True'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['bambu_oembed']