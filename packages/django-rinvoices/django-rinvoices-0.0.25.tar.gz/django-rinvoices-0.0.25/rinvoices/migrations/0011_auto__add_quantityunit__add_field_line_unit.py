# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'QuantityUnit'
        db.create_table('rinvoices_quantityunit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('rinvoices', ['QuantityUnit'])

        # Adding field 'Line.unit'
        db.add_column('rinvoices_line', 'unit',
                      self.gf('django.db.models.fields.related.ForeignKey')(default='', related_name='quantityunit', blank=True, to=orm['rinvoices.QuantityUnit']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'QuantityUnit'
        db.delete_table('rinvoices_quantityunit')

        # Deleting field 'Line.unit'
        db.delete_column('rinvoices_line', 'unit_id')


    models = {
        'rinvoices.currency': {
            'Meta': {'object_name': 'Currency'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'toeuro': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'rinvoices.customer': {
            'Meta': {'object_name': 'Customer'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'cif': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'rinvoices.header': {
            'Meta': {'object_name': 'Header'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'cif': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'more': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rinvoices.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'charged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'currency'", 'to': "orm['rinvoices.Currency']"}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'customer'", 'to': "orm['rinvoices.Customer']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'header': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'header'", 'to': "orm['rinvoices.Header']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_number': ('django.db.models.fields.IntegerField', [], {}),
            'registered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'subtotal': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'subtotal_iva': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'taxes': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'taxes'", 'to': "orm['rinvoices.Tax']"}),
            'total': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        'rinvoices.invoicereceive': {
            'Meta': {'object_name': 'InvoiceReceive'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'default': "''", 'related_name': "'provider'", 'blank': 'True', 'to': "orm['rinvoices.Provider']"}),
            'reference': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'registered': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'total': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        },
        'rinvoices.line': {
            'Meta': {'object_name': 'Line'},
            'amount': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'concept': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'line'", 'to': "orm['rinvoices.Invoice']"}),
            'quantity': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'default': "''", 'related_name': "'quantityunit'", 'blank': 'True', 'to': "orm['rinvoices.QuantityUnit']"}),
            'unit_price': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'rinvoices.provider': {
            'Meta': {'object_name': 'Provider'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'cif': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'rinvoices.quantityunit': {
            'Meta': {'object_name': 'QuantityUnit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'rinvoices.tax': {
            'Meta': {'object_name': 'Tax'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['rinvoices']