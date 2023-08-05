# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('freckle_budgets', '0004_projectmonth_overhead_previous_month'),
    ]

    operations = [
        migrations.CreateModel(
            name='FreeTime',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day', models.DateField(verbose_name='Day')),
                ('is_public_holiday', models.BooleanField(default=False, verbose_name='Is public holiday')),
                ('is_sick_leave', models.BooleanField(default=False, verbose_name='Is sick leave')),
                ('employee', models.ForeignKey(verbose_name='Employee', to='freckle_budgets.Employee')),
            ],
            options={
                'ordering': ['employee', '-day'],
            },
            bases=(models.Model,),
        ),
    ]
