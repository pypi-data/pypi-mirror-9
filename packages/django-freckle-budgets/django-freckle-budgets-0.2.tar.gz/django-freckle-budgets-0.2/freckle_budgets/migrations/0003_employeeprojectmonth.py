# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('freckle_budgets', '0002_employee'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeProjectMonth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('responsibility', models.PositiveIntegerField(help_text='Positive integer (1-100%)', verbose_name='Responsibility')),
                ('employee', models.ForeignKey(related_name='employee_project_months', verbose_name='Employee', to='freckle_budgets.Employee')),
                ('project_month', models.ForeignKey(related_name='employee_project_months', verbose_name='ProjectMonth', to='freckle_budgets.ProjectMonth')),
            ],
            options={
                'ordering': ['project_month__project', 'employee'],
            },
            bases=(models.Model,),
        ),
    ]
