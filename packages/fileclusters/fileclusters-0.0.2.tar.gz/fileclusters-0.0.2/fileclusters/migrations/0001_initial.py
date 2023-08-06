# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ClusterConffile'
        db.create_table('fileclusters_clusterconffile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=500)),
        ))
        db.send_create_signal('fileclusters', ['ClusterConffile'])

        # Adding model 'Component'
        db.create_table('fileclusters_component', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cluster', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fileclusters.ClusterConffile'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=500)),
            ('master', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('fileclusters', ['Component'])

        # Adding model 'Agent'
        db.create_table('fileclusters_agent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('port', self.gf('django.db.models.fields.IntegerField')()),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=1024)),
        ))
        db.send_create_signal('fileclusters', ['Agent'])

        # Adding M2M table for field components on 'Agent'
        db.create_table('fileclusters_agent_components', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('agent', models.ForeignKey(orm['fileclusters.agent'], null=False)),
            ('component', models.ForeignKey(orm['fileclusters.component'], null=False))
        ))
        db.create_unique('fileclusters_agent_components', ['agent_id', 'component_id'])

        # Adding model 'Conffile'
        db.create_table('fileclusters_conffile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('component', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fileclusters.Component'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=1024)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=1024)),
            ('parser', self.gf('django.db.models.fields.CharField')(max_length=512)),
        ))
        db.send_create_signal('fileclusters', ['Conffile'])

        # Adding model 'HTTPService'
        db.create_table('fileclusters_httpservice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('component', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fileclusters.Component'])),
            ('auth_method', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('url_basename', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('fileclusters', ['HTTPService'])

        # Adding model 'HTTPAuthData'
        db.create_table('fileclusters_httpauthdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('http_service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fileclusters.HTTPService'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('fileclusters', ['HTTPAuthData'])

        # Adding model 'ServiceUser'
        db.create_table('fileclusters_serviceuser', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('revocated', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('caid', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('privatekey', self.gf('django.db.models.fields.TextField')()),
            ('publickey', self.gf('django.db.models.fields.TextField')()),
            ('passp12', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('passauth', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('end_time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('fileclusters', ['ServiceUser'])

        # Adding model 'Service'
        db.create_table('fileclusters_service', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('component', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fileclusters.Component'])),
            ('urischeme', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('urihost', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('uriport', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('uripath', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('serverdir', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('servertype', self.gf('django.db.models.fields.CharField')(default='fullApp', max_length=1000)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('passfile', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('passfileperm', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('passfileowner', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('revocatefile', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('revocatefileperm', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('revocatefileowner', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal('fileclusters', ['Service'])

        # Adding model 'UserPermission'
        db.create_table('fileclusters_userpermission', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fileclusters.ServiceUser'])),
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fileclusters.Service'])),
            ('directory', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('mode', self.gf('django.db.models.fields.CharField')(default='ro', max_length=1000)),
        ))
        db.send_create_signal('fileclusters', ['UserPermission'])

        # Adding model 'ApacheSVNService'
        db.create_table('fileclusters_apachesvnservice', (
            ('service_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['fileclusters.Service'], unique=True, primary_key=True)),
            ('svnpassfile', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('svnpassfileperm', self.gf('django.db.models.fields.PositiveSmallIntegerField')(max_length=1000)),
            ('svnpassfileowner', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal('fileclusters', ['ApacheSVNService'])

        # Adding model 'SSLProxyX509AuthService'
        db.create_table('fileclusters_sslproxyx509authservice', (
            ('service_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['fileclusters.Service'], unique=True, primary_key=True)),
            ('delegate', self.gf('django.db.models.fields.related.ForeignKey')(related_name='delegate', to=orm['fileclusters.Service'])),
            ('server_type', self.gf('django.db.models.fields.CharField')(default='nginx', max_length=1000)),
            ('serverpass', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal('fileclusters', ['SSLProxyX509AuthService'])

        # Adding model 'ServiceConfSource'
        db.create_table('fileclusters_serviceconfsource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('service_conf_source_type', self.gf('django.db.models.fields.CharField')(default='none', max_length=1000)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('port', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('directory', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=1000)),
        ))
        db.send_create_signal('fileclusters', ['ServiceConfSource'])


    def backwards(self, orm):
        # Deleting model 'ClusterConffile'
        db.delete_table('fileclusters_clusterconffile')

        # Deleting model 'Component'
        db.delete_table('fileclusters_component')

        # Deleting model 'Agent'
        db.delete_table('fileclusters_agent')

        # Removing M2M table for field components on 'Agent'
        db.delete_table('fileclusters_agent_components')

        # Deleting model 'Conffile'
        db.delete_table('fileclusters_conffile')

        # Deleting model 'HTTPService'
        db.delete_table('fileclusters_httpservice')

        # Deleting model 'HTTPAuthData'
        db.delete_table('fileclusters_httpauthdata')

        # Deleting model 'ServiceUser'
        db.delete_table('fileclusters_serviceuser')

        # Deleting model 'Service'
        db.delete_table('fileclusters_service')

        # Deleting model 'UserPermission'
        db.delete_table('fileclusters_userpermission')

        # Deleting model 'ApacheSVNService'
        db.delete_table('fileclusters_apachesvnservice')

        # Deleting model 'SSLProxyX509AuthService'
        db.delete_table('fileclusters_sslproxyx509authservice')

        # Deleting model 'ServiceConfSource'
        db.delete_table('fileclusters_serviceconfsource')


    models = {
        'fileclusters.agent': {
            'Meta': {'object_name': 'Agent'},
            'components': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['fileclusters.Component']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1024'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'port': ('django.db.models.fields.IntegerField', [], {}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'fileclusters.apachesvnservice': {
            'Meta': {'object_name': 'ApacheSVNService', '_ormbases': ['fileclusters.Service']},
            'service_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fileclusters.Service']", 'unique': 'True', 'primary_key': 'True'}),
            'svnpassfile': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'svnpassfileowner': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'svnpassfileperm': ('django.db.models.fields.PositiveSmallIntegerField', [], {'max_length': '1000'})
        },
        'fileclusters.clusterconffile': {
            'Meta': {'object_name': 'ClusterConffile'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'fileclusters.component': {
            'Meta': {'object_name': 'Component'},
            'cluster': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fileclusters.ClusterConffile']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'master': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'fileclusters.conffile': {
            'Meta': {'object_name': 'Conffile'},
            'component': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fileclusters.Component']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '1024'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parser': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'fileclusters.httpauthdata': {
            'Meta': {'object_name': 'HTTPAuthData'},
            'http_service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fileclusters.HTTPService']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'fileclusters.httpservice': {
            'Meta': {'object_name': 'HTTPService'},
            'auth_method': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'component': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fileclusters.Component']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url_basename': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'fileclusters.service': {
            'Meta': {'object_name': 'Service'},
            'component': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fileclusters.Component']"}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
        'fileclusters.serviceconfsource': {
            'Meta': {'object_name': 'ServiceConfSource'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'directory': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'port': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'service_conf_source_type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '1000'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '1000'})
        },
        'fileclusters.serviceuser': {
            'Meta': {'object_name': 'ServiceUser'},
            'caid': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'end_time': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'passauth': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'passp12': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'privatekey': ('django.db.models.fields.TextField', [], {}),
            'publickey': ('django.db.models.fields.TextField', [], {}),
            'revocated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'fileclusters.sslproxyx509authservice': {
            'Meta': {'object_name': 'SSLProxyX509AuthService', '_ormbases': ['fileclusters.Service']},
            'delegate': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'delegate'", 'to': "orm['fileclusters.Service']"}),
            'server_type': ('django.db.models.fields.CharField', [], {'default': "'nginx'", 'max_length': '1000'}),
            'serverpass': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'service_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['fileclusters.Service']", 'unique': 'True', 'primary_key': 'True'})
        },
        'fileclusters.userpermission': {
            'Meta': {'object_name': 'UserPermission'},
            'directory': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.CharField', [], {'default': "'ro'", 'max_length': '1000'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fileclusters.Service']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fileclusters.ServiceUser']"})
        }
    }

    complete_apps = ['fileclusters']