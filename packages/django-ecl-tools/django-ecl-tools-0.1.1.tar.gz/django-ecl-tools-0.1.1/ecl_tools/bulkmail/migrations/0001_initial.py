# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'List'
        db.create_table(u'bulkmail_list', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('from_name', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('reply_to', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('mail_domain', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('address', self.gf('django.db.models.fields.TextField')()),
            ('short_description', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('frequency', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('sorder', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'bulkmail', ['List'])

        # Adding model 'Subscription'
        db.create_table(u'bulkmail_subscription', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bulk_list', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bulkmail.List'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('email_status', self.gf('django.db.models.fields.CharField')(default='no-process', max_length=255, null=True, blank=True)),
            ('is_clean', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('signup_location', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('bounce1', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('bounce2', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('complaint', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('unsubscribed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'bulkmail', ['Subscription'])

        # Adding model 'Optin'
        db.create_table(u'bulkmail_optin', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('skey', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('signup_location', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'bulkmail', ['Optin'])

        # Adding M2M table for field bulk_lists on 'Optin'
        m2m_table_name = db.shorten_name(u'bulkmail_optin_bulk_lists')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('optin', models.ForeignKey(orm[u'bulkmail.optin'], null=False)),
            ('list', models.ForeignKey(orm[u'bulkmail.list'], null=False))
        ))
        db.create_unique(m2m_table_name, ['optin_id', 'list_id'])

        # Adding model 'Campaign'
        db.create_table(u'bulkmail_campaign', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('bulk_list', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bulkmail.List'])),
            ('html', self.gf('django.db.models.fields.TextField')()),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('sent', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('scheduled', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'bulkmail', ['Campaign'])

        # Adding model 'TrackingEvent'
        db.create_table(u'bulkmail_trackingevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['bulkmail.Subscription'])),
            ('campaign', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('event', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('client_os', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('client_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('client_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('device_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('user_agent', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('region', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('ip', self.gf('django.db.models.fields.CharField')(max_length=15)),
        ))
        db.send_create_signal(u'bulkmail', ['TrackingEvent'])


    def backwards(self, orm):
        # Deleting model 'List'
        db.delete_table(u'bulkmail_list')

        # Deleting model 'Subscription'
        db.delete_table(u'bulkmail_subscription')

        # Deleting model 'Optin'
        db.delete_table(u'bulkmail_optin')

        # Removing M2M table for field bulk_lists on 'Optin'
        db.delete_table(db.shorten_name(u'bulkmail_optin_bulk_lists'))

        # Deleting model 'Campaign'
        db.delete_table(u'bulkmail_campaign')

        # Deleting model 'TrackingEvent'
        db.delete_table(u'bulkmail_trackingevent')


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
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'client_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'client_os': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'client_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'device_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['bulkmail.Subscription']"}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['bulkmail']