# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Contact.form_name'
        db.add_column(u'cmsplugin_contact', 'form_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Contact.form_name'
        db.delete_column(u'cmsplugin_contact', 'form_name')


    models = {
        'cms.cmsplugin': {
            'Meta': {'object_name': 'CMSPlugin'},
            'changed_date': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.CMSPlugin']", 'null': 'True', 'blank': 'True'}),
            'placeholder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cms.Placeholder']", 'null': 'True'}),
            'plugin_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            'position': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'rght': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'})
        },
        'cms.placeholder': {
            'Meta': {'object_name': 'Placeholder'},
            'default_width': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slot': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'cmsplugin_contact.contact': {
            'Meta': {'object_name': 'Contact', 'db_table': "u'cmsplugin_contact'"},
            'akismet_api_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'cmsplugin_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['cms.CMSPlugin']", 'unique': 'True', 'primary_key': 'True'}),
            'content_label': ('django.db.models.fields.CharField', [], {'default': "u'Message'", 'max_length': '100'}),
            'email_label': ('django.db.models.fields.CharField', [], {'default': "u'Your email address'", 'max_length': '100'}),
            'form_name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'recaptcha_private_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'recaptcha_public_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'recaptcha_theme': ('django.db.models.fields.CharField', [], {'default': "'clean'", 'max_length': '20'}),
            'site_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'spam_protection_method': ('django.db.models.fields.SmallIntegerField', [], {'default': '0'}),
            'subject_label': ('django.db.models.fields.CharField', [], {'default': "u'Subject'", 'max_length': '200'}),
            'submit': ('django.db.models.fields.CharField', [], {'default': "u'Submit'", 'max_length': '30'}),
            'thanks': ('django.db.models.fields.TextField', [], {'default': "u'Thank you for your message.'", 'max_length': '200'})
        }
    }

    complete_apps = ['cmsplugin_contact']