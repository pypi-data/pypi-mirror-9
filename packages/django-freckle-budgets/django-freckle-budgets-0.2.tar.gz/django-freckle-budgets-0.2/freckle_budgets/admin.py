"""Admin classes for the freckle_budgets app."""
from django.contrib import admin

from . import models


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'freckle_id']


class EmployeeProjectMonthAdmin(admin.ModelAdmin):
    list_display = ['project_month', 'employee', 'responsibility']
    raw_id_fields = ['project_month']


class EmployeeProjectMonthInline(admin.TabularInline):
    model = models.EmployeeProjectMonth


class FreeTimeAdmin(admin.ModelAdmin):
    list_display = ['employee', 'day']
    list_filter = ['employee', ]


class MonthAdmin(admin.ModelAdmin):
    list_display = ['year', 'month', 'employees', 'public_holidays']


class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'freckle_project_id', 'color', 'is_investment']


class ProjectMonthAdmin(admin.ModelAdmin):
    list_display = [
        'month', 'project', 'budget', 'overhead_previous_month', 'rate']
    list_filter = ['project', ]
    inlines = [EmployeeProjectMonthInline, ]


class YearAdmin(admin.ModelAdmin):
    list_display = ['year', 'sick_leave_days', 'vacation_days']


admin.site.register(models.Employee, EmployeeAdmin)
admin.site.register(models.EmployeeProjectMonth, EmployeeProjectMonthAdmin)
admin.site.register(models.FreeTime, FreeTimeAdmin)
admin.site.register(models.Month, MonthAdmin)
admin.site.register(models.Project, ProjectAdmin)
admin.site.register(models.ProjectMonth, ProjectMonthAdmin)
admin.site.register(models.Year, YearAdmin)
