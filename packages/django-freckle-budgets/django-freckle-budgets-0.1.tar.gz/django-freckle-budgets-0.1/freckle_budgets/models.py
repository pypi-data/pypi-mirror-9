"""Models for the freckle_budgets app."""
import calendar
import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Year(models.Model):
    year = models.PositiveIntegerField(verbose_name=_('Year'))
    rate = models.FloatField(default=100, verbose_name=_('Rate'))
    work_hours_per_day = models.FloatField(
        default=5, verbose_name=_('Work hours per day'))
    sick_leave_days = models.PositiveIntegerField(
        verbose_name=_('Sick leave days'))
    vacation_days = models.PositiveIntegerField(
        verbose_name=_('Vacation days'))

    class Meta:
        ordering = ['-year', ]

    def __str__(self):
        return str(self.year)


class MonthManager(models.Manager):
    def get_months_with_projects(self, year):
        qs = self.get_queryset()
        return qs.filter(year__year=year, projectmonth__isnull=False).order_by(
            'month').distinct()


@python_2_unicode_compatible
class Month(models.Model):
    year = models.ForeignKey(Year, verbose_name=_('Year'))
    month = models.PositiveIntegerField(verbose_name=_('Month'))
    employees = models.FloatField(
        default=1, verbose_name=_('Number of employees'))
    public_holidays = models.PositiveIntegerField(
        verbose_name=_('Public holydays'), default=0, null=True)

    objects = MonthManager()

    class Meta:
        ordering = ['-year', 'month']

    def __str__(self):
        return '{0} {1}'.format(self.month, self.year)

    def get_available_ressources(self):
        """Returns the available hours that the team can work this month."""
        work_days = self.get_work_days()
        work_hours = self.year.work_hours_per_day * work_days * self.employees
        return work_hours

    def get_cashflow_projects(self):
        return ProjectMonth.objects.filter(month=self).exclude(
            project__is_investment=True).order_by('-budget', )

    def get_date(self):
        return datetime.date(self.year.year, self.month, 1)

    def get_investment_projects(self):
        return ProjectMonth.objects.filter(
            month=self, project__is_investment=True).order_by('-budget', )

    def get_total_cashflow_hours(self):
        projects = self.get_cashflow_projects()
        hours = 0
        for project in projects:
            hours += project.get_budget_hours()
        return hours

    def get_total_investment_hours(self):
        projects = self.get_investment_projects()
        hours = 0
        for project in projects:
            hours += project.get_budget_hours()
        return hours

    def get_total_investment(self):
        projects = self.get_investment_projects()
        profit = 0
        for project in projects:
            profit += project.budget
        return profit

    def get_total_profit(self):
        projects = self.get_cashflow_projects()
        profit = 0
        for project in projects:
            profit += project.budget
        return profit

    def get_unused_hours(self):
        projects = ProjectMonth.objects.filter(month=self)
        used_hours = 0
        for project in projects:
            used_hours += project.get_budget_hours()
        unused_hours = self.get_available_ressources() - used_hours
        return unused_hours

    def get_unused_daily_hours(self):
        unused_hours = self.get_unused_hours()
        return unused_hours / self.get_work_days()

    def get_unused_budget(self):
        return self.get_unused_hours() * self.year.rate

    def get_weekdays(self):
        """Returns the number of weekdays of this month."""
        month_dates = calendar.Calendar(0).itermonthdates(
            self.year.year, self.month)
        weekdays = 0
        for day in month_dates:
            if day.month != self.month:
                continue
            if day.weekday() < 5:
                weekdays += 1
        return weekdays

    def get_work_days(self):
        work_days = self.get_weekdays() * 1.0
        work_days -= self.public_holidays
        work_days -= self.year.sick_leave_days / 12
        work_days -= self.year.vacation_days / 12
        return work_days


@python_2_unicode_compatible
class Project(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    freckle_project_id = models.CharField(
        max_length=256, verbose_name=_('Freckle project ID'), null=True)
    color = models.CharField(max_length=100, verbose_name=_('Color'))
    is_investment = models.BooleanField(
        default=False, verbose_name=_('Is investment'))

    class Meta:
        ordering = ['name', ]

    def __str__(self):
        return self.name


class ProjectMonthManager(models.Manager):
    def get_project_months(self, year):
        result = []
        months = Month.objects.get_months_with_projects(year)
        for month in months:
            project_months = self.get_queryset().filter(month=month)
            result.append([month, project_months])
        return result

    def get_freckle_projects(self, year):
        qs = self.get_queryset()
        return qs.filter(month__year__year=year).order_by(
            'project__freckle_project_id').values_list(
                'project__freckle_project_id', flat=True).distinct()


@python_2_unicode_compatible
class ProjectMonth(models.Model):
    project = models.ForeignKey(
        Project, verbose_name=('Project'), related_name='project_months')
    month = models.ForeignKey(Month, verbose_name=('Month'))
    budget = models.FloatField(verbose_name=_('Budget'))
    rate = models.FloatField(verbose_name=_('Rate'))

    objects = ProjectMonthManager()

    class Meta:
        ordering = ['-month', 'project']

    def __str__(self):
        return '{0} - {1}'.format(self.project, self.month)

    def get_budget_hours(self):
        """Returns the budget hours based on the budget and the rate."""
        return self.budget / self.rate

    def get_daily_hours(self):
        """Returns the daily hours needed in order to use up the budget."""
        budget_hours = self.get_budget_hours()
        return budget_hours / self.month.get_work_days()
