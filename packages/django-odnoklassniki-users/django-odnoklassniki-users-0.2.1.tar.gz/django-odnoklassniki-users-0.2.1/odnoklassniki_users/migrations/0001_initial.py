# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'odnoklassniki_users_user', (
            ('fetched', self.gf('django.db.models.fields.DateTimeField')(db_index=True, null=True, blank=True)),
            ('id', self.gf('django.db.models.fields.BigIntegerField')(primary_key=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('shortname', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('gender', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True)),
            ('birthday', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('country_code', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('locale', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('photo_id', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('current_status', self.gf('django.db.models.fields.TextField')()),
            ('current_status_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('current_status_id', self.gf('django.db.models.fields.BigIntegerField')(null=True)),
            ('allows_anonym_access', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('has_email', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('has_service_invisible', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('private', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('last_online', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('registered_date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('pic1024x768', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('pic128max', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('pic128x128', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('pic180min', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('pic190x190', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('pic240min', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('pic320min', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('pic50x50', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('pic640x480', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('url_profile', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('url_profile_mobile', self.gf('django.db.models.fields.URLField')(max_length=200)),
        ))
        db.send_create_signal(u'odnoklassniki_users', ['User'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'odnoklassniki_users_user')


    models = {
        u'odnoklassniki_users.user': {
            'Meta': {'object_name': 'User'},
            'allows_anonym_access': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'current_status': ('django.db.models.fields.TextField', [], {}),
            'current_status_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'current_status_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'fetched': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'gender': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            'has_email': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'has_service_invisible': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.BigIntegerField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'last_online': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'locale': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'photo_id': ('django.db.models.fields.BigIntegerField', [], {'null': 'True'}),
            'pic1024x768': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'pic128max': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'pic128x128': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'pic180min': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'pic190x190': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'pic240min': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'pic320min': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'pic50x50': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'pic640x480': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'private': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'registered_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'shortname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'url_profile': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'url_profile_mobile': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['odnoklassniki_users']