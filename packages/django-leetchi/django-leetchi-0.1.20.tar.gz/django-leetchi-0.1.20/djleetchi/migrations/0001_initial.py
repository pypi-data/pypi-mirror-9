# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Contribution'
        db.create_table('leetchi_contribution', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('contribution', self.gf('djleetchi.fields.ResourceField')()),
            ('wallet', self.gf('djleetchi.fields.ResourceField')()),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('client_fee_amount', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('return_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('template_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('is_completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_success', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('type', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=1, db_index=True)),
        ))
        db.send_create_signal(u'djleetchi', ['Contribution'])

        # Adding model 'Transfer'
        db.create_table('leetchi_transfer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('transfer', self.gf('djleetchi.fields.ResourceField')()),
            ('beneficiary_wallet', self.gf('djleetchi.fields.ResourceField')()),
            ('payer', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payers', to=orm['auth.User'])),
            ('beneficiary', self.gf('django.db.models.fields.related.ForeignKey')(related_name='beneficiaries', to=orm['auth.User'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'djleetchi', ['Transfer'])

        # Adding model 'TransferRefund'
        db.create_table(u'djleetchi_transferrefund', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('transfer_refund', self.gf('djleetchi.fields.ResourceField')()),
            ('transfer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djleetchi.Transfer'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal(u'djleetchi', ['TransferRefund'])

        # Adding model 'Refund'
        db.create_table('leetchi_refund', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('refund', self.gf('djleetchi.fields.ResourceField')()),
            ('contribution', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djleetchi.Contribution'])),
            ('is_success', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'djleetchi', ['Refund'])

        # Adding model 'Beneficiary'
        db.create_table('leetchi_beneficiary', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('beneficiary', self.gf('djleetchi.fields.ResourceField')()),
            ('bank_account_owner_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('bank_account_owner_address', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('bank_account_iban', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('bank_account_bic', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'djleetchi', ['Beneficiary'])

        # Adding model 'Withdrawal'
        db.create_table(u'djleetchi_withdrawal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('amount', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('client_fee_amount', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('beneficiary', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['djleetchi.Beneficiary'], null=True, blank=True)),
            ('withdrawal', self.gf('djleetchi.fields.ResourceField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('wallet', self.gf('djleetchi.fields.ResourceField')(null=True, blank=True)),
            ('is_completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_succeeded', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'djleetchi', ['Withdrawal'])

        # Adding model 'Wallet'
        db.create_table('leetchi_wallet', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('user', self.gf('djleetchi.fields.ResourceField')(null=True, blank=True)),
            ('wallet', self.gf('djleetchi.fields.ResourceField')(null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('last_synced', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'djleetchi', ['Wallet'])

        # Adding unique constraint on 'Wallet', fields ['wallet', 'content_type', 'object_id']
        db.create_unique('leetchi_wallet', ['wallet_id', 'content_type_id', 'object_id'])

        # Adding model 'StrongAuthentication'
        db.create_table('leetchi_strongauthentication', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('strong_authentication', self.gf('djleetchi.fields.ResourceField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('beneficiary', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='strong_authentication', null=True, to=orm['djleetchi.Beneficiary'])),
            ('is_completed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_succeeded', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'djleetchi', ['StrongAuthentication'])


    def backwards(self, orm):
        # Removing unique constraint on 'Wallet', fields ['wallet', 'content_type', 'object_id']
        db.delete_unique('leetchi_wallet', ['wallet_id', 'content_type_id', 'object_id'])

        # Deleting model 'Contribution'
        db.delete_table('leetchi_contribution')

        # Deleting model 'Transfer'
        db.delete_table('leetchi_transfer')

        # Deleting model 'TransferRefund'
        db.delete_table(u'djleetchi_transferrefund')

        # Deleting model 'Refund'
        db.delete_table('leetchi_refund')

        # Deleting model 'Beneficiary'
        db.delete_table('leetchi_beneficiary')

        # Deleting model 'Withdrawal'
        db.delete_table(u'djleetchi_withdrawal')

        # Deleting model 'Wallet'
        db.delete_table('leetchi_wallet')

        # Deleting model 'StrongAuthentication'
        db.delete_table('leetchi_strongauthentication')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('sluggable.fields.SluggableField', [], {'unique': 'True', 'max_length': '50', 'populate_from': 'None'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'djleetchi.beneficiary': {
            'Meta': {'object_name': 'Beneficiary', 'db_table': "'leetchi_beneficiary'"},
            'bank_account_bic': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'bank_account_iban': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'bank_account_owner_address': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'bank_account_owner_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'beneficiary': ('djleetchi.fields.ResourceField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'djleetchi.contribution': {
            'Meta': {'object_name': 'Contribution', 'db_table': "'leetchi_contribution'"},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'client_fee_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'contribution': ('djleetchi.fields.ResourceField', [], {}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_success': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'return_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'template_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'wallet': ('djleetchi.fields.ResourceField', [], {})
        },
        u'djleetchi.refund': {
            'Meta': {'object_name': 'Refund', 'db_table': "'leetchi_refund'"},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'contribution': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['djleetchi.Contribution']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_success': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'refund': ('djleetchi.fields.ResourceField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'djleetchi.strongauthentication': {
            'Meta': {'object_name': 'StrongAuthentication', 'db_table': "'leetchi_strongauthentication'"},
            'beneficiary': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'strong_authentication'", 'null': 'True', 'to': u"orm['djleetchi.Beneficiary']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_succeeded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'strong_authentication': ('djleetchi.fields.ResourceField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'djleetchi.transfer': {
            'Meta': {'object_name': 'Transfer', 'db_table': "'leetchi_transfer'"},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'beneficiary': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'beneficiaries'", 'to': u"orm['auth.User']"}),
            'beneficiary_wallet': ('djleetchi.fields.ResourceField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'payer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payers'", 'to': u"orm['auth.User']"}),
            'transfer': ('djleetchi.fields.ResourceField', [], {})
        },
        u'djleetchi.transferrefund': {
            'Meta': {'object_name': 'TransferRefund'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'transfer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['djleetchi.Transfer']"}),
            'transfer_refund': ('djleetchi.fields.ResourceField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'djleetchi.wallet': {
            'Meta': {'unique_together': "(('wallet', 'content_type', 'object_id'),)", 'object_name': 'Wallet', 'db_table': "'leetchi_wallet'"},
            'amount': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_synced': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('djleetchi.fields.ResourceField', [], {'null': 'True', 'blank': 'True'}),
            'wallet': ('djleetchi.fields.ResourceField', [], {'null': 'True', 'blank': 'True'})
        },
        u'djleetchi.withdrawal': {
            'Meta': {'object_name': 'Withdrawal'},
            'amount': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'beneficiary': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['djleetchi.Beneficiary']", 'null': 'True', 'blank': 'True'}),
            'client_fee_amount': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_succeeded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'wallet': ('djleetchi.fields.ResourceField', [], {'null': 'True', 'blank': 'True'}),
            'withdrawal': ('djleetchi.fields.ResourceField', [], {})
        }
    }

    complete_apps = ['djleetchi']