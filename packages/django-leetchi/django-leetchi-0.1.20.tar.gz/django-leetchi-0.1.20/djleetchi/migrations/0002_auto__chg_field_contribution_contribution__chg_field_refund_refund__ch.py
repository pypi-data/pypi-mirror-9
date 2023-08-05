# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Contribution.contribution'
        db.alter_column('leetchi_contribution', 'contribution_id', self.gf('djleetchi.fields.ResourceField')(null=True))

        # Changing field 'Refund.refund'
        db.alter_column('leetchi_refund', 'refund_id', self.gf('djleetchi.fields.ResourceField')(null=True))

        # Changing field 'Withdrawal.withdrawal'
        db.alter_column(u'leetchi_withdrawal', 'withdrawal_id', self.gf('djleetchi.fields.ResourceField')(null=True))

        # Changing field 'Beneficiary.beneficiary'
        db.alter_column('leetchi_beneficiary', 'beneficiary_id', self.gf('djleetchi.fields.ResourceField')(null=True))

        # Changing field 'StrongAuthentication.strong_authentication'
        db.alter_column('leetchi_strongauthentication', 'strong_authentication_id', self.gf('djleetchi.fields.ResourceField')(null=True))

        # Changing field 'Transfer.transfer'
        db.alter_column('leetchi_transfer', 'transfer_id', self.gf('djleetchi.fields.ResourceField')(null=True))

        # Changing field 'TransferRefund.transfer_refund'
        db.alter_column(u'leetchi_transferrefund', 'transfer_refund_id', self.gf('djleetchi.fields.ResourceField')(null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Contribution.contribution'
        raise RuntimeError("Cannot reverse this migration. 'Contribution.contribution' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Contribution.contribution'
        db.alter_column('leetchi_contribution', 'contribution_id', self.gf('djleetchi.fields.ResourceField')())

        # User chose to not deal with backwards NULL issues for 'Refund.refund'
        raise RuntimeError("Cannot reverse this migration. 'Refund.refund' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Refund.refund'
        db.alter_column('leetchi_refund', 'refund_id', self.gf('djleetchi.fields.ResourceField')())

        # User chose to not deal with backwards NULL issues for 'Withdrawal.withdrawal'
        raise RuntimeError("Cannot reverse this migration. 'Withdrawal.withdrawal' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Withdrawal.withdrawal'
        db.alter_column(u'leetchi_withdrawal', 'withdrawal_id', self.gf('djleetchi.fields.ResourceField')())

        # User chose to not deal with backwards NULL issues for 'Beneficiary.beneficiary'
        raise RuntimeError("Cannot reverse this migration. 'Beneficiary.beneficiary' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Beneficiary.beneficiary'
        db.alter_column('leetchi_beneficiary', 'beneficiary_id', self.gf('djleetchi.fields.ResourceField')())

        # User chose to not deal with backwards NULL issues for 'StrongAuthentication.strong_authentication'
        raise RuntimeError("Cannot reverse this migration. 'StrongAuthentication.strong_authentication' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'StrongAuthentication.strong_authentication'
        db.alter_column('leetchi_strongauthentication', 'strong_authentication_id', self.gf('djleetchi.fields.ResourceField')())

        # User chose to not deal with backwards NULL issues for 'Transfer.transfer'
        raise RuntimeError("Cannot reverse this migration. 'Transfer.transfer' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Transfer.transfer'
        db.alter_column('leetchi_transfer', 'transfer_id', self.gf('djleetchi.fields.ResourceField')())

        # User chose to not deal with backwards NULL issues for 'TransferRefund.transfer_refund'
        raise RuntimeError("Cannot reverse this migration. 'TransferRefund.transfer_refund' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'TransferRefund.transfer_refund'
        db.alter_column(u'leetchi_transferrefund', 'transfer_refund_id', self.gf('djleetchi.fields.ResourceField')())

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
            'beneficiary': ('djleetchi.fields.ResourceField', [], {'null': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'djleetchi.contribution': {
            'Meta': {'object_name': 'Contribution', 'db_table': "'leetchi_contribution'"},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'client_fee_amount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'contribution': ('djleetchi.fields.ResourceField', [], {'null': 'True'}),
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
            'refund': ('djleetchi.fields.ResourceField', [], {'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'djleetchi.strongauthentication': {
            'Meta': {'object_name': 'StrongAuthentication', 'db_table': "'leetchi_strongauthentication'"},
            'beneficiary': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'strong_authentication'", 'null': 'True', 'to': u"orm['djleetchi.Beneficiary']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_completed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_succeeded': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'strong_authentication': ('djleetchi.fields.ResourceField', [], {'null': 'True'}),
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
            'transfer': ('djleetchi.fields.ResourceField', [], {'null': 'True'})
        },
        u'djleetchi.transferrefund': {
            'Meta': {'object_name': 'TransferRefund'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'transfer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['djleetchi.Transfer']"}),
            'transfer_refund': ('djleetchi.fields.ResourceField', [], {'null': 'True'}),
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
            'withdrawal': ('djleetchi.fields.ResourceField', [], {'null': 'True'})
        }
    }

    complete_apps = ['djleetchi']
