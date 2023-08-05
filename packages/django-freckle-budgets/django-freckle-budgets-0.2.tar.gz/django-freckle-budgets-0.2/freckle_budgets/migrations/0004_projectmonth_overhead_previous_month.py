# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('freckle_budgets', '0003_employeeprojectmonth'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectmonth',
            name='overhead_previous_month',
            field=models.FloatField(null=True, verbose_name='Overhead previous month', blank=True),
            preserve_default=True,
        ),
    ]
