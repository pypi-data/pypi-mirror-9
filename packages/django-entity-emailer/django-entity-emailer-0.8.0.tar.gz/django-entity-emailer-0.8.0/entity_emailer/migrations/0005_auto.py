# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding M2M table for field recipients on 'Email'
        m2m_table_name = db.shorten_name(u'entity_emailer_email_recipients')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('email', models.ForeignKey(orm[u'entity_emailer.email'], null=False)),
            ('entity', models.ForeignKey(orm[u'entity.entity'], null=False))
        ))
        db.create_unique(m2m_table_name, ['email_id', 'entity_id'])


    def backwards(self, orm):
        # Removing M2M table for field recipients on 'Email'
        db.delete_table(db.shorten_name(u'entity_emailer_email_recipients'))


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'entity.entity': {
            'Meta': {'unique_together': "(('entity_id', 'entity_type', 'entity_kind'),)", 'object_name': 'Entity'},
            'display_name': ('django.db.models.fields.TextField', [], {'db_index': 'True', 'blank': 'True'}),
            'entity_id': ('django.db.models.fields.IntegerField', [], {}),
            'entity_kind': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity.EntityKind']", 'on_delete': 'models.PROTECT'}),
            'entity_meta': ('jsonfield.fields.JSONField', [], {'null': 'True'}),
            'entity_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'on_delete': 'models.PROTECT'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'})
        },
        u'entity.entitykind': {
            'Meta': {'object_name': 'EntityKind'},
            'display_name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '256', 'db_index': 'True'})
        },
        u'entity_emailer.email': {
            'Meta': {'object_name': 'Email'},
            'context': ('jsonfield.fields.JSONField', [], {}),
            'from_address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'recipients': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'+'", 'symmetrical': 'False', 'to': u"orm['entity.Entity']"}),
            'scheduled': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.utcnow', 'null': 'True'}),
            'send_to': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity.Entity']"}),
            'sent': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity_subscription.Source']"}),
            'subentity_kind': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['entity.EntityKind']", 'null': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entity_emailer.EmailTemplate']"}),
            'uid': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '100', 'unique': 'True', 'null': 'True'})
        },
        u'entity_emailer.emailtemplate': {
            'Meta': {'object_name': 'EmailTemplate'},
            'context_loader': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256', 'blank': 'True'}),
            'html_template': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'html_template_path': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'text_template': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'text_template_path': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '256'})
        },
        u'entity_subscription.source': {
            'Meta': {'object_name': 'Source'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'})
        }
    }

    complete_apps = ['entity_emailer']