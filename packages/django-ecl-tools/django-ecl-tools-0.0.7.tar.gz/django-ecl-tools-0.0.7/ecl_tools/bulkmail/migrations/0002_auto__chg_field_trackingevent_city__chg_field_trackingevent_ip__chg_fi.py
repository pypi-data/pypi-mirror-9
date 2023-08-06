# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'TrackingEvent.city'
        db.alter_column(u'bulkmail_trackingevent', 'city', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'TrackingEvent.ip'
        db.alter_column(u'bulkmail_trackingevent', 'ip', self.gf('django.db.models.fields.CharField')(max_length=15, null=True))

        # Changing field 'TrackingEvent.client_name'
        db.alter_column(u'bulkmail_trackingevent', 'client_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'TrackingEvent.client_os'
        db.alter_column(u'bulkmail_trackingevent', 'client_os', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'TrackingEvent.client_type'
        db.alter_column(u'bulkmail_trackingevent', 'client_type', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'TrackingEvent.user_agent'
        db.alter_column(u'bulkmail_trackingevent', 'user_agent', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

        # Changing field 'TrackingEvent.device_type'
        db.alter_column(u'bulkmail_trackingevent', 'device_type', self.gf('django.db.models.fields.CharField')(max_length=50, null=True))

        # Changing field 'TrackingEvent.country'
        db.alter_column(u'bulkmail_trackingevent', 'country', self.gf('django.db.models.fields.CharField')(max_length=10, null=True))

        # Changing field 'TrackingEvent.region'
        db.alter_column(u'bulkmail_trackingevent', 'region', self.gf('django.db.models.fields.CharField')(max_length=10, null=True))

    def backwards(self, orm):

        # Changing field 'TrackingEvent.city'
        db.alter_column(u'bulkmail_trackingevent', 'city', self.gf('django.db.models.fields.CharField')(default='', max_length=50))

        # Changing field 'TrackingEvent.ip'
        db.alter_column(u'bulkmail_trackingevent', 'ip', self.gf('django.db.models.fields.CharField')(default='', max_length=15))

        # Changing field 'TrackingEvent.client_name'
        db.alter_column(u'bulkmail_trackingevent', 'client_name', self.gf('django.db.models.fields.CharField')(default='', max_length=50))

        # Changing field 'TrackingEvent.client_os'
        db.alter_column(u'bulkmail_trackingevent', 'client_os', self.gf('django.db.models.fields.CharField')(default='', max_length=50))

        # Changing field 'TrackingEvent.client_type'
        db.alter_column(u'bulkmail_trackingevent', 'client_type', self.gf('django.db.models.fields.CharField')(default='', max_length=50))

        # Changing field 'TrackingEvent.user_agent'
        db.alter_column(u'bulkmail_trackingevent', 'user_agent', self.gf('django.db.models.fields.CharField')(default='', max_length=200))

        # Changing field 'TrackingEvent.device_type'
        db.alter_column(u'bulkmail_trackingevent', 'device_type', self.gf('django.db.models.fields.CharField')(default='', max_length=50))

        # Changing field 'TrackingEvent.country'
        db.alter_column(u'bulkmail_trackingevent', 'country', self.gf('django.db.models.fields.CharField')(default='', max_length=10))

        # Changing field 'TrackingEvent.region'
        db.alter_column(u'bulkmail_trackingevent', 'region', self.gf('django.db.models.fields.CharField')(default='', max_length=10))

    models = {
        u'bulkmail.campaign': {
            'Meta': {'ordering': "('-created',)", 'object_name': 'Campaign'},
            'bulk_list': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bulkmail.List']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'html': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scheduled': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'bulkmail.list': {
            'Meta': {'ordering': "('sorder',)", 'object_name': 'List'},
            'address': ('django.db.models.fields.TextField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'frequency': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'from_name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mail_domain': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'reply_to': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'short_description': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'sorder': ('django.db.models.fields.IntegerField', [], {})
        },
        u'bulkmail.optin': {
            'Meta': {'object_name': 'Optin'},
            'bulk_lists': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['bulkmail.List']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signup_location': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'skey': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'bulkmail.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'bounce1': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'bounce2': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'bulk_list': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bulkmail.List']"}),
            'complaint': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'email_status': ('django.db.models.fields.CharField', [], {'default': "'no-process'", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_clean': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'signup_location': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'unsubscribed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'bulkmail.trackingevent': {
            'Meta': {'object_name': 'TrackingEvent'},
            'campaign': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'client_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'client_os': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'client_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'device_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bulkmail.Subscription']"}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['bulkmail']