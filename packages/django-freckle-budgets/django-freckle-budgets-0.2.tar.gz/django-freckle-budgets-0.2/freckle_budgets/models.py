"""Models for the freckle_budgets app."""
import calendar
import datetime

from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Employee(models.Model):
    name = models.CharField(max_length=256, verbose_name=_('Name'))
    freckle_id = models.CharField(max_length=256, verbose_name=_('Freckle ID'))

    class Meta:
        ordering = ['name', ]

    def __str__(self):
        return str(self.name)

    def get_employee_project_months(self, month):
        """
        Returns the projects this employee is responsible for in this month.

        """
        return EmployeeProjectMonth.objects.filter(
            employee=self, project_month__month=month)


@python_2_unicode_compatible
class FreeTime(models.Model):
    employee = models.ForeignKey(Employee, verbose_name=_('Employee'))
    day = models.DateField(
        verbose_name=_('Day'))
    is_public_holiday = models.BooleanField(
        verbose_name=_('Is public holiday'), default=False)
    is_sick_leave = models.BooleanField(
        verbose_name=_('Is sick leave'), default=False)

    class Meta:
        ordering = ['employee', '-day']

    def __str__(self):
        return '{0} - {1}'.format(self.employee, self.day)


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

    def get_total_cashflow_budget(self):
        return ProjectMonth.objects.filter(
            month__year=self, project__is_investment=False).aggregate(
                Sum('budget'))['budget__sum']

    def get_total_investment_budget(self):
        return ProjectMonth.objects.filter(
            month__year=self, project__is_investment=True).aggregate(
                Sum('budget'))['budget__sum']

    def get_total_unused_budget(self):
        result = 0
        for month in Month.objects.filter(year=self):
            result += month.get_unused_budget()
        return result


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

    def get_available_ressources_max(self):
        """Returns the available hours that the team can work this month."""
        work_days = self.get_work_days(
            minus_sick_leave=False, minus_vacations=False)
        work_hours = self.year.work_hours_per_day * work_days * self.employees
        return work_hours

    def get_available_ressources_max_per_person(self):
        """Returns the hours that each employee should work this month."""
        return self.get_available_ressources_max() / self.employees * 1.0

    def get_average_rate(self):
        """Returns the average rate for all cashflow projects of this month."""
        return self.get_total_profit() / self.get_total_cashflow_hours()

    def get_cashflow_projects(self):
        return ProjectMonth.objects.filter(month=self).exclude(
            project__is_investment=True).order_by('-budget', )

    def get_date(self):
        return datetime.date(self.year.year, self.month, 1)

    def get_employees(self):
        """
        Returns all employees that have projects scheduled for this month.

        """
        employee_pks = EmployeeProjectMonth.objects.filter(
            project_month__month=self).values_list(
                'employee__pk', flat=True).distinct()
        return Employee.objects.filter(pk__in=employee_pks)

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

    def get_work_days(self, minus_sick_leave=True, minus_vacations=True):
        """
        Returns the work days that should be used in whole-year-calculations.

        Public holidays, sick leave days and vacation days will be deducted.

        :minus_sick_leave: If ``False``, sick leave will not be deducted from
          the total work days.
        :minus_vacations: If ``False``, vacations will not be deducted from
          the total work days.

        """
        work_days = self.get_weekdays() * 1.0
        work_days -= self.public_holidays
        if minus_sick_leave:
            work_days -= self.year.sick_leave_days / 12
        if minus_vacations:
            work_days -= self.year.vacation_days / 12
        return work_days

    def get_work_days_max(self):
        """
        Returns the maximum work days, if no one falls sick or takes vacations.

        """
        return self.get_work_days(
            minus_sick_leave=False, minus_vacations=False)

    def get_workloads(self):
        """
        Returns the workload for all employees for this month.

        The workload is an amount of hours that the employee needs to work per
        available work day in order to meet all planned budgets.

        The workload is calculated as follows:

        * Project1: Budget = 1000
        * Project1: Rate = 100
        * Project1: Budget time = 10 hours
        * Employee responsibility for the project: 50%
        * Available work days for the month: 18
        * Employee work load = 10 / 18 * 0.5 = 0.28

        The result looks like this:

            {
                employee_freckle_id: {
                    'name': Heino,
                    'cashflow_workload': 4,
                    'investment_workload': 2,
                    'total_workload': 6,
                },
                employee_freckle_id: { ... },
                ...
            }

        """
        result = {}
        employee_project_months = EmployeeProjectMonth.objects.filter(
            project_month__month=self)
        for epm in employee_project_months:
            if epm.employee.freckle_id not in result:
                result[epm.employee.freckle_id] = {
                    'name': epm.employee.name,
                    'cashflow_workload': 0,
                    'investment_workload': 0,
                    'total_workload': 0,
                }

            daily_hours = epm.project_month.get_daily_hours()
            if epm.project_month.project.is_investment:
                key = 'investment_workload'
            else:
                key = 'cashflow_workload'

            workload = daily_hours * (epm.responsibility / 100.0)
            result[epm.employee.freckle_id][key] += workload
            result[epm.employee.freckle_id]['total_workload'] += workload
        return result


class ProjectManager(models.Manager):
    def get_for_year(self, year):
        qs = self.get_queryset()
        qs = qs.filter(
            project_months__month__year__year__exact=year).distinct()
        return qs


@python_2_unicode_compatible
class Project(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    freckle_project_id = models.CharField(
        max_length=256, verbose_name=_('Freckle project ID'), null=True)
    color = models.CharField(max_length=100, verbose_name=_('Color'))
    is_investment = models.BooleanField(
        default=False, verbose_name=_('Is investment'))

    objects = ProjectManager()

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
    """
    Contains the budget for a certain project in a certain month.

    :project: A ``Project`` instance.
    :month: A ``Month`` instance.
    :budget: The budget for this porject in this month.
    :rate: The rate that can be billed for this project in this month. Budget
      divided by rate equals ``budget_hours``.
    :overhead_previous_month: Sometimes you have already worked hours on this
      project in the previous month. Enter the amount of dollars that can be
      deducted from this month's budget so that the hours achieved looks more
      realistic.

    """
    project = models.ForeignKey(
        Project, verbose_name=('Project'), related_name='project_months')
    month = models.ForeignKey(Month, verbose_name=('Month'))
    budget = models.FloatField(verbose_name=_('Budget'))
    rate = models.FloatField(verbose_name=_('Rate'))
    overhead_previous_month = models.FloatField(
        verbose_name=_('Overhead previous month'), blank=True, null=True)

    objects = ProjectMonthManager()

    class Meta:
        ordering = ['-month', 'project']

    def __str__(self):
        return '{0} - {1}'.format(self.project, self.month)

    def get_budget_hours(self):
        """Returns the budget hours based on the budget and the rate."""
        overhead = self.overhead_previous_month
        if overhead is None:
            overhead = 0
        return (self.budget - overhead) / self.rate

    def get_daily_hours(self):
        """Returns the daily hours needed in order to use up the budget."""
        budget_hours = self.get_budget_hours()
        return budget_hours / self.month.get_work_days()


@python_2_unicode_compatible
class EmployeeProjectMonth(models.Model):
    project_month = models.ForeignKey(
        ProjectMonth, verbose_name=_('ProjectMonth'),
        related_name='employee_project_months')
    employee = models.ForeignKey(
        Employee, verbose_name=_('Employee'),
        related_name='employee_project_months')
    responsibility = models.PositiveIntegerField(
        verbose_name=_('Responsibility'),
        help_text=_('Positive integer (1-100%)'))

    class Meta:
        ordering = ['project_month__project', 'employee']

    def __str__(self):
        return '{0} - {1}'.format(self.project_month, self.employee)

    def get_budget_hours(self):
        """
        Returns the total hours the employee should be working on this project.

        Based on the project's budget and the responsibility of this employee.

        """
        budget_hours = self.project_month.get_budget_hours()
        return budget_hours * (self.responsibility / 100.0)
