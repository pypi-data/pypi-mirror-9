# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'storage_tank_maintenance.description'
        db.alter_column('main_storage_tank_maintenance', 'description', self.gf('django.db.models.fields.CharField')(max_length=800, null=True))

        # Changing field 'chassis_maintenance_Service.service'
        db.alter_column('main_chassis_maintenance_service', 'service', self.gf('django.db.models.fields.CharField')(max_length=1500))

        # Changing field 'radio_maintenance.description'
        db.alter_column('main_radio_maintenance', 'description', self.gf('django.db.models.fields.CharField')(max_length=800))

        # Changing field 'chassis_maintenance.description'
        db.alter_column('main_chassis_maintenance', 'description', self.gf('django.db.models.fields.CharField')(max_length=800, null=True))

        # Changing field 'carburetion_tank_maintenance.description'
        db.alter_column('main_carburetion_tank_maintenance', 'description', self.gf('django.db.models.fields.CharField')(max_length=800, null=True))

    def backwards(self, orm):

        # Changing field 'storage_tank_maintenance.description'
        db.alter_column('main_storage_tank_maintenance', 'description', self.gf('django.db.models.fields.CharField')(max_length=150, null=True))

        # Changing field 'chassis_maintenance_Service.service'
        db.alter_column('main_chassis_maintenance_service', 'service', self.gf('django.db.models.fields.CharField')(max_length=150))

        # Changing field 'radio_maintenance.description'
        db.alter_column('main_radio_maintenance', 'description', self.gf('django.db.models.fields.CharField')(max_length=150))

        # Changing field 'chassis_maintenance.description'
        db.alter_column('main_chassis_maintenance', 'description', self.gf('django.db.models.fields.CharField')(max_length=150, null=True))

        # Changing field 'carburetion_tank_maintenance.description'
        db.alter_column('main_carburetion_tank_maintenance', 'description', self.gf('django.db.models.fields.CharField')(max_length=150, null=True))

    models = {
        'main.carburetion_tank': {
            'Meta': {'object_name': 'carburetion_tank'},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'capacity': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'default': "'G'", 'max_length': '10'}),
            'fill_valve': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'safety_valve': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'series': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'service_valve': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '10'}),
            'ten_percent_valve': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'main.carburetion_tank_maintenance': {
            'Meta': {'object_name': 'carburetion_tank_maintenance'},
            'carburetion_tank': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.carburetion_tank']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'garage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.garage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'main.carburetion_tank_s': {
            'Meta': {'object_name': 'carburetion_tank_S'},
            'carburetion_tank_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.carburetion_tank_maintenance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.service']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.carburetion_tank_sg': {
            'Meta': {'object_name': 'carburetion_tank_SG'},
            'carburetion_tank_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.carburetion_tank_maintenance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'services_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.services_group']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.chassis': {
            'Meta': {'object_name': 'chassis'},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'color': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license_plates': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'line': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'mileage': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '10'})
        },
        'main.chassis_maintenance': {
            'Meta': {'object_name': 'chassis_maintenance'},
            'chassis': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.chassis']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'garage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.garage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mileage': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'main.chassis_maintenance_s': {
            'Meta': {'object_name': 'chassis_maintenance_S'},
            'chassis_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.chassis_maintenance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.service']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.chassis_maintenance_service': {
            'Meta': {'object_name': 'chassis_maintenance_Service'},
            'chassis_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.chassis_maintenance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.CharField', [], {'max_length': '1500'})
        },
        'main.chassis_maintenance_sg': {
            'Meta': {'object_name': 'chassis_maintenance_SG'},
            'chassis_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.chassis_maintenance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'services_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.services_group']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.garage': {
            'Meta': {'object_name': 'garage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'office_phone': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'})
        },
        'main.radio': {
            'Meta': {'object_name': 'radio'},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'series': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '10'})
        },
        'main.radio_maintenance': {
            'Meta': {'object_name': 'radio_maintenance'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '800'}),
            'garage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.garage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'radio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.radio']", 'null': 'True', 'blank': 'True'})
        },
        'main.radio_maintenance_s': {
            'Meta': {'object_name': 'radio_maintenance_S'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'radio_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.radio_maintenance']"}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.service']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.radio_maintenance_sg': {
            'Meta': {'object_name': 'radio_maintenance_SG'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'radio_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.radio_maintenance']"}),
            'services_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.services_group']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'})
        },
        'main.service': {
            'Meta': {'object_name': 'service'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'service_type': ('django.db.models.fields.CharField', [], {'default': "'CH'", 'max_length': '10'})
        },
        'main.services_group': {
            'Meta': {'object_name': 'services_group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'main.services_group_items': {
            'Meta': {'object_name': 'services_group_items'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'services': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.service']"}),
            'services_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.services_group']"})
        },
        'main.storage_tank': {
            'Meta': {'object_name': 'storage_tank'},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'capArt': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'check_look_valve': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'excess_steam_valve': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'fill_valve': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'no_recoil_valve': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'overfill_valve': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'safety_valve': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'series': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'service_valve': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'N'", 'max_length': '10'}),
            'ten_percent_valve': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'water_nominal_cap': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'main.storage_tank_maintenance': {
            'Meta': {'object_name': 'storage_tank_maintenance'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '800', 'null': 'True', 'blank': 'True'}),
            'garage': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.garage']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'storage_tank': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.storage_tank']", 'null': 'True', 'blank': 'True'})
        },
        'main.storage_tank_maintenance_s': {
            'Meta': {'object_name': 'storage_tank_maintenance_S'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.service']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'storage_tank_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.storage_tank_maintenance']"})
        },
        'main.storage_tank_maintenance_sg': {
            'Meta': {'object_name': 'storage_tank_maintenance_SG'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'services_group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.services_group']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'storage_tank_maintenance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.storage_tank_maintenance']"})
        },
        'main.vehicle': {
            'Meta': {'object_name': 'vehicle'},
            'carburetion_tank': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.carburetion_tank']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'chassis': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.chassis']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'radio': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.radio']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'storage_tank': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.storage_tank']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'vehicle_type': ('django.db.models.fields.CharField', [], {'default': "'PIG'", 'max_length': '10'})
        }
    }

    complete_apps = ['main']