# flake8: noqa
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EmployeeProjectMonth'
        db.create_table(u'freckle_budgets_employeeprojectmonth', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project_month', self.gf('django.db.models.fields.related.ForeignKey')(related_name='employee_project_months', to=orm['freckle_budgets.ProjectMonth'])),
            ('employee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='employee_project_months', to=orm['freckle_budgets.Employee'])),
            ('responsibility', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal(u'freckle_budgets', ['EmployeeProjectMonth'])


    def backwards(self, orm):
        # Deleting model 'EmployeeProjectMonth'
        db.delete_table(u'freckle_budgets_employeeprojectmonth')


    models = {
        u'freckle_budgets.employee': {
            'Meta': {'ordering': "['name']", 'object_name': 'Employee'},
            'freckle_id': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'freckle_budgets.employeeprojectmonth': {
            'Meta': {'ordering': "['project_month__project', 'employee']", 'object_name': 'EmployeeProjectMonth'},
            'employee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'employee_project_months'", 'to': u"orm['freckle_budgets.Employee']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project_month': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'employee_project_months'", 'to': u"orm['freckle_budgets.ProjectMonth']"}),
            'responsibility': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        u'freckle_budgets.month': {
            'Meta': {'ordering': "['-year', 'month']", 'object_name': 'Month'},
            'employees': ('django.db.models.fields.FloatField', [], {'default': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'public_holidays': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'null': 'True'}),
            'year': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['freckle_budgets.Year']"})
        },
        u'freckle_budgets.project': {
            'Meta': {'ordering': "['name']", 'object_name': 'Project'},
            'color': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'freckle_project_id': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_investment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'freckle_budgets.projectmonth': {
            'Meta': {'ordering': "['-month', 'project']", 'object_name': 'ProjectMonth'},
            'budget': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'month': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['freckle_budgets.Month']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'project_months'", 'to': u"orm['freckle_budgets.Project']"}),
            'rate': ('django.db.models.fields.FloatField', [], {})
        },
        u'freckle_budgets.year': {
            'Meta': {'ordering': "['-year']", 'object_name': 'Year'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'rate': ('django.db.models.fields.FloatField', [], {'default': '100'}),
            'sick_leave_days': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'vacation_days': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'work_hours_per_day': ('django.db.models.fields.FloatField', [], {'default': '5'}),
            'year': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['freckle_budgets']
