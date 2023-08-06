# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.db.utils import OperationalError
from django.db import connection

class Migration(SchemaMigration):

    def db_table_exists(self, table_name):
        return table_name in connection.introspection.table_names()


    def forwards(self, orm):
        # Adding model 'MailConfirmation'
        try:
            if not self.db_table_exists('mail_confirmation_mailconfirmation'):
                db.create_table(u'mail_confirmation_mailconfirmation', (
                    (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                    ('confirmationid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
                    ('confirmed', self.gf('django.db.models.fields.BooleanField')(default=False)),
                    ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
                    ('confirm_success_template', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
                    ('confirm_success_url', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
                    ('toconfirm_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
                    ('toconfirm_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
                ))
                db.send_create_signal(u'mail_confirmation', ['MailConfirmation'])
        except OperationalError:
            # table already exists
            pass

    def backwards(self, orm):
        # Deleting model 'MailConfirmation'
        db.delete_table(u'mail_confirmation_mailconfirmation')


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'mail_confirmation.mailconfirmation': {
            'Meta': {'object_name': 'MailConfirmation'},
            'confirm_success_template': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'confirm_success_url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'confirmationid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'toconfirm_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'toconfirm_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"})
        }
    }

    complete_apps = ['mail_confirmation']
