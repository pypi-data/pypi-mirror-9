#@PydevCodeAnalysisIgnore
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.utils import timezone

def mysql_quotes(sql):
    if 'mysql' in db.backend_name.lower():
        return sql.replace('"', '`')
    else:
        return sql

class Migration(SchemaMigration):
    
    
    def forwards(self, orm):
        
        if not db.dry_run:
            keyID = 0
            vCode = ''
            characterID = 0
            sql = mysql_quotes('SELECT "keyID", "vCode", "characterID" FROM "common_apikey";')
            rows = db.execute(sql)
            if rows:
                keyID, vCode, characterID = rows[0]
                keyID = int(keyID)
                vCode = str(vCode)
                characterID = int(characterID)

        # Deleting model 'APIKey'
        db.delete_table('common_apikey')

        # Adding model 'Setting'
        db.create_table('common_setting', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, primary_key=True)),
            ('value', self.gf('django.db.models.fields.CharField')(default='', max_length=1000)),
        ))
        db.send_create_signal('common', ['Setting'])

        if not db.dry_run:
            orm.Setting.objects.create(name='common_api_keyID', value=repr(keyID))
            orm.Setting.objects.create(name='common_api_vCode', value=repr(vCode))
            orm.Setting.objects.create(name='common_api_characterID', value=repr(characterID))


    def backwards(self, orm):
        if not db.dry_run:
            keyID = 0
            vCode = ''
            characterID = 0
            settings = ['common_api_keyID', 'common_api_vCode', 'common_api_characterID']
            sql = 'SELECT "name", "value" FROM "common_setting" WHERE "name" IN %s;'
            rows = db.execute(mysql_quotes(sql), [settings])
            for name, value in rows:
                if name == 'common_api_keyID':
                    keyID = eval(value)
                elif name == 'common_api_vCode':
                    vCode = eval(value)
                elif name == 'common_api_characterID':
                    characterID = eval(value)

        # Adding model 'APIKey'
        db.create_table('common_apikey', (
            ('vCode', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('keyID', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('characterID', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('common', ['APIKey'])

        # Deleting model 'Setting'
        db.delete_table('common_setting')

        if not db.dry_run:
            orm.APIKey.objects.create(name='', keyID=keyID, vCode=vCode, characterID=characterID)

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'timezone.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'timezone.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'common.colorthreshold': {
            'Meta': {'object_name': 'ColorThreshold'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'threshold': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'common.externalapplication': {
            'Meta': {'object_name': 'ExternalApplication'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '1024'})
        },
        'common.groupbinding': {
            'Meta': {'object_name': 'GroupBinding'},
            'external_app': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_bindings'", 'to': "orm['common.ExternalApplication']"}),
            'external_id': ('django.db.models.fields.IntegerField', [], {}),
            'external_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bindings'", 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'common.registrationprofile': {
            'Meta': {'object_name': 'RegistrationProfile'},
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'common.setting': {
            'Meta': {'ordering': "['name']", 'object_name': 'Setting'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1000'})
        },
        'common.updatedate': {
            'Meta': {'ordering': "['-update_date']", 'object_name': 'UpdateDate'},
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'prev_update': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'update_date': ('django.db.models.fields.DateTimeField', [], {})
        },
        'common.urlpermission': {
            'Meta': {'object_name': 'UrlPermission'},
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'allowed_urls'", 'symmetrical': 'False', 'to': "orm['auth.Group']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pattern': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'common.userapikey': {
            'Meta': {'ordering': "['user']", 'object_name': 'UserAPIKey'},
            'is_valid': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'keyID': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'eve_accounts'", 'to': "orm['auth.User']"}),
            'vCode': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'common.userbinding': {
            'Meta': {'object_name': 'UserBinding'},
            'external_app': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_bindings'", 'to': "orm['common.ExternalApplication']"}),
            'external_id': ('django.db.models.fields.IntegerField', [], {}),
            'external_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'bindings'", 'to': "orm['auth.User']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['common']
