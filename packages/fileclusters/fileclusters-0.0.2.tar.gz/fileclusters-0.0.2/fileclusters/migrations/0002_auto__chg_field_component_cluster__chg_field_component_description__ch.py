# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Component.cluster'
        db.alter_column(u'fileclusters_component', 'cluster_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fileclusters.ClusterConffile'], null=True))

        # Changing field 'Component.description'
        db.alter_column(u'fileclusters_component', 'description', self.gf('django.db.models.fields.TextField')(max_length=500, null=True))

        # Changing field 'Component.name'
        db.alter_column(u'fileclusters_component', 'name', self.gf('django.db.models.fields.CharField')(max_length=200, null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Component.cluster'
        raise RuntimeError("Cannot reverse this migration. 'Component.cluster' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Component.cluster'
        db.alter_column(u'fileclusters_component', 'cluster_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fileclusters.ClusterConffile']))

        # User chose to not deal with backwards NULL issues for 'Component.description'
        raise RuntimeError("Cannot reverse this migration. 'Component.description' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Component.description'
        db.alter_column(u'fileclusters_component', 'description', self.gf('django.db.models.fields.TextField')(max_length=500))

        # User chose to not deal with backwards NULL issues for 'Component.name'
        raise RuntimeError("Cannot reverse this migration. 'Component.name' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Component.name'
        db.alter_column(u'fileclusters_component', 'name', self.gf('django.db.models.fields.CharField')(max_length=200))

    models = {
        u'fileclusters.agent': {
            'Meta': {'object_name': 'Agent'},
            'components': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['fileclusters.Component']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1024'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        u'fileclusters.apachesvnservice': {
            'Meta': {'object_name': 'ApacheSVNService', '_ormbases': [u'fileclusters.Service']},
            u'service_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['fileclusters.Service']", 'unique': 'True', 'primary_key': 'True'}),
            'svnpassfile': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'svnpassfileowner': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'svnpassfileperm': ('django.db.models.fields.PositiveSmallIntegerField', [], {'max_length': '1000'})
        },
        u'fileclusters.clusterconffile': {
            'Meta': {'object_name': 'ClusterConffile'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'fileclusters.component': {
            'Meta': {'object_name': 'Component'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fileclusters.ClusterConffile']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '500', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.BooleanField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'fileclusters.conffile': {
            'Meta': {'object_name': 'Conffile'},
            'component': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fileclusters.Component']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1024'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parser': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        u'fileclusters.httpauthdata': {
            'Meta': {'object_name': 'HTTPAuthData'},
            'http_service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fileclusters.HTTPService']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'fileclusters.httpservice': {
            'Meta': {'object_name': 'HTTPService'},
            'auth_method': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'component': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fileclusters.Component']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url_basename': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'fileclusters.service': {
            'Meta': {'object_name': 'Service'},
            'component': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fileclusters.Component']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'passfile': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'passfileowner': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'passfileperm': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'revocatefile': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'revocatefileowner': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'revocatefileperm': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'serverdir': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'servertype': ('django.db.models.fields.CharField', [], {'default': "'fullApp'", 'max_length': '1000'}),
            'urihost': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'uripath': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'uriport': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'urischeme': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        u'fileclusters.serviceconfsource': {
            'Meta': {'object_name': 'ServiceConfSource'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'directory': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'port': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'service_conf_source_type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '1000'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        u'fileclusters.serviceuser': {
            'Meta': {'object_name': 'ServiceUser'},
            'caid': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'passauth': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'passp12': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'privatekey': ('django.db.models.fields.TextField', [], {}),
            'publickey': ('django.db.models.fields.TextField', [], {}),
            'revocated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'fileclusters.sslproxyx509authservice': {
            'Meta': {'object_name': 'SSLProxyX509AuthService', '_ormbases': [u'fileclusters.Service']},
            'delegate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'delegate'", 'to': u"orm['fileclusters.Service']"}),
            'server_type': ('django.db.models.fields.CharField', [], {'default': "'nginx'", 'max_length': '1000'}),
            'serverpass': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'service_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['fileclusters.Service']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'fileclusters.userpermission': {
            'Meta': {'object_name': 'UserPermission'},
            'directory': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'default': "'ro'", 'max_length': '1000'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fileclusters.Service']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['fileclusters.ServiceUser']"})
        }
    }

    complete_apps = ['fileclusters']