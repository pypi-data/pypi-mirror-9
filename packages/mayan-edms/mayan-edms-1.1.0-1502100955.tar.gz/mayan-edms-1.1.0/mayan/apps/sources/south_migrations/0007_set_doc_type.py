# -*- coding: utf-8 -*-
from south.v2 import DataMigration
from django.db import models


def fake_get_or_create(model, *args, **kwargs):
    try:
        obj = model.objects.get(**kwargs)
    except model.DoesNotExist:
        obj = model(**kwargs)
        obj.save()
    return obj


class Migration(DataMigration):
    needed_by = (
        ('documents', '0024_auto__add_field_documenttype_ocr'),
    )

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        orphan_doc_type = fake_get_or_create(orm['documents.DocumentType'], name='_orphan_document_')
        orm.IntervalBaseModel.objects.filter(document_type__isnull=True).update(document_type=orphan_doc_type)

    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'documents.documenttype': {
            'Meta': {'ordering': "['name']", 'object_name': 'DocumentType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        u'sources.emailbasemodel': {
            'Meta': {'ordering': "('title',)", 'object_name': 'EmailBaseModel', '_ormbases': [u'sources.IntervalBaseModel']},
            'host': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'intervalbasemodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sources.IntervalBaseModel']", 'unique': 'True', 'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '96'}),
            'port': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ssl': ('django.db.models.fields.BooleanField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '96'})
        },
        u'sources.imapemail': {
            'Meta': {'ordering': "('title',)", 'object_name': 'IMAPEmail', '_ormbases': [u'sources.EmailBaseModel']},
            u'emailbasemodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sources.EmailBaseModel']", 'unique': 'True', 'primary_key': 'True'}),
            'mailbox': ('django.db.models.fields.CharField', [], {'default': "'INBOX'", 'max_length': '64'})
        },
        u'sources.interactivesource': {
            'Meta': {'ordering': "('title',)", 'object_name': 'InteractiveSource', '_ormbases': [u'sources.Source']},
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sources.Source']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'sources.intervalbasemodel': {
            'Meta': {'ordering': "('title',)", 'object_name': 'IntervalBaseModel', '_ormbases': [u'sources.OutOfProcessSource']},
            'document_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['documents.DocumentType']"}),
            'interval': ('django.db.models.fields.PositiveIntegerField', [], {'default': '60'}),
            u'outofprocesssource_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sources.OutOfProcessSource']", 'unique': 'True', 'primary_key': 'True'}),
            'uncompress': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'sources.outofprocesssource': {
            'Meta': {'ordering': "('title',)", 'object_name': 'OutOfProcessSource', '_ormbases': [u'sources.Source']},
            u'source_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sources.Source']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'sources.pop3email': {
            'Meta': {'ordering': "('title',)", 'object_name': 'POP3Email', '_ormbases': [u'sources.EmailBaseModel']},
            u'emailbasemodel_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sources.EmailBaseModel']", 'unique': 'True', 'primary_key': 'True'}),
            'timeout': ('django.db.models.fields.PositiveIntegerField', [], {'default': '60'})
        },
        u'sources.source': {
            'Meta': {'ordering': "('title',)", 'object_name': 'Source'},
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        u'sources.sourcetransformation': {
            'Meta': {'ordering': "('order',)", 'object_name': 'SourceTransformation'},
            'arguments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'transformation': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        },
        u'sources.stagingfoldersource': {
            'Meta': {'ordering': "('title',)", 'object_name': 'StagingFolderSource', '_ormbases': [u'sources.InteractiveSource']},
            'delete_after_upload': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'folder_path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'interactivesource_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sources.InteractiveSource']", 'unique': 'True', 'primary_key': 'True'}),
            'preview_height': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'preview_width': ('django.db.models.fields.IntegerField', [], {}),
            'uncompress': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'sources.watchfoldersource': {
            'Meta': {'ordering': "('title',)", 'object_name': 'WatchFolderSource', '_ormbases': [u'sources.OutOfProcessSource']},
            'delete_after_upload': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'folder_path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'interval': ('django.db.models.fields.PositiveIntegerField', [], {}),
            u'outofprocesssource_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sources.OutOfProcessSource']", 'unique': 'True', 'primary_key': 'True'}),
            'uncompress': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        },
        u'sources.webformsource': {
            'Meta': {'ordering': "('title',)", 'object_name': 'WebFormSource', '_ormbases': [u'sources.InteractiveSource']},
            u'interactivesource_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sources.InteractiveSource']", 'unique': 'True', 'primary_key': 'True'}),
            'uncompress': ('django.db.models.fields.CharField', [], {'max_length': '1'})
        }
    }

    complete_apps = ['sources']
    symmetrical = True
