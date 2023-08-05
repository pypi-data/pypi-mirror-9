# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Month',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.PositiveIntegerField(verbose_name='Month')),
                ('employees', models.FloatField(default=1, verbose_name='Number of employees')),
                ('public_holidays', models.PositiveIntegerField(default=0, null=True, verbose_name='Public holydays')),
            ],
            options={
                'ordering': ['-year', 'month'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('freckle_project_id', models.CharField(max_length=256, null=True, verbose_name='Freckle project ID')),
                ('color', models.CharField(max_length=100, verbose_name='Color')),
                ('is_investment', models.BooleanField(default=False, verbose_name='Is investment')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectMonth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('budget', models.FloatField(verbose_name='Budget')),
                ('rate', models.FloatField(verbose_name='Rate')),
                ('month', models.ForeignKey(verbose_name=b'Month', to='freckle_budgets.Month')),
                ('project', models.ForeignKey(related_name='project_months', verbose_name=b'Project', to='freckle_budgets.Project')),
            ],
            options={
                'ordering': ['-month', 'project'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Year',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.PositiveIntegerField(verbose_name='Year')),
                ('rate', models.FloatField(default=100, verbose_name='Rate')),
                ('work_hours_per_day', models.FloatField(default=5, verbose_name='Work hours per day')),
                ('sick_leave_days', models.PositiveIntegerField(verbose_name='Sick leave days')),
                ('vacation_days', models.PositiveIntegerField(verbose_name='Vacation days')),
            ],
            options={
                'ordering': ['-year'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='month',
            name='year',
            field=models.ForeignKey(verbose_name='Year', to='freckle_budgets.Year'),
            preserve_default=True,
        ),
    ]
