"""Tests for the models of the freckle_budgets app."""
import datetime

from django.test import TestCase

from mixer.backend.django import mixer

from . import fixtures
from .. import models


class EmployeeTestCase(TestCase):
    """Tests for the ``Employee`` model."""
    longMessage = True

    def test_class(self):
        obj = mixer.blend('freckle_budgets.Employee')
        self.assertTrue(obj.pk, msg=('Object can be saved'))
        self.assertEqual(obj.__str__(), str(obj.name), msg=(
            '__str__ should return correct string'))

    def test_get_employee_project_months(self):
        fixtures.create_employee_project_months(self)
        result = self.employee1.get_employee_project_months(self.month)
        self.assertEqual(result.count(), 1, msg=(
            'Should return the projects this employee is responsible for'
            ' during this month'))


class FreeTimeTestCase(TestCase):
    """Tests for the ``FreeTime`` model."""
    longMessage = True

    def test_class(self):
        obj = mixer.blend('freckle_budgets.FreeTime')
        self.assertTrue(obj.pk, msg=('Object can be saved'))
        expected = '{0} - {1}'.format(obj.employee, obj.day)
        self.assertEqual(obj.__str__(), expected, msg=(
            '__str__ should return correct string'))


class YearTestCase(TestCase):
    """Tests for the ``Year`` model."""
    longMessage = True

    def test_model(self):
        obj = mixer.blend('freckle_budgets.Year')
        self.assertTrue(obj.pk, msg=('Object can be saved'))
        self.assertEqual(obj.__str__(), str(obj.year), msg=(
            '__str__ should return correct string'))

    def test_get_total_cashflow_budget(self):
        fixtures.create_project_months(self)
        result = self.year.get_total_cashflow_budget()
        self.assertEqual(result, 3000, msg=(
            'Should add up all planned budgets for all projects that have'
            ' is_investment==False for this year'))

    def test_get_total_investment_budget(self):
        fixtures.create_project_months(self)
        result = self.year.get_total_investment_budget()
        self.assertEqual(result, 4000, msg=(
            'Should add up all planned budgets for all projects that have'
            ' is_investment==True for this year'))

    def test_get_total_unused_budget(self):
        fixtures.create_project_months(self)
        result = self.year.get_total_unused_budget()
        self.assertEqual(result, 31000, msg=(
            'Should add up all unused budgets for all months of the year'))


class MonthManagerTestCase(TestCase):
    """Tests for the ``MonthManager`` model manager."""
    longMessage = True

    def test_get_months_with_projects(self):
        fixtures.create_project_months(self)
        mixer.blend('freckle_budgets.Month', month=3, year=self.year)

        manager = models.Month.objects
        result = manager.get_months_with_projects(2015)
        self.assertEqual(result.count(), 2, msg=(
            'Should return all months that have a project'))


class MonthTestCase(TestCase):
    """Tests for the ``Month`` model."""
    longMessage = True

    def test_model(self):
        obj = mixer.blend('freckle_budgets.Month')
        self.assertTrue(obj.pk, msg=('Obj can be saved'))

        expected = '{0} {1}'.format(obj.month, obj.year)
        self.assertEqual(obj.__str__(), expected, msg=(
            '__str__ should return correct string'))

    def test_get_available_ressources(self):
        fixtures.create_month(self)
        result = self.month.get_available_ressources()
        self.assertEqual(result, 190, msg=(
            'January has 22 work days. Minus holidays, vacations and sick'
            ' leave, 19 days remain. Multiplied with the daily hours (5) and'
            ' number of employees (2), the result should be 19 * 5 * 2 = 190'))

    def test_get_available_ressources_max(self):
        fixtures.create_month(self)
        result = self.month.get_available_ressources_max()
        self.assertEqual(result, 210, msg=(
            'January has 22 work days. Minus holidays, 21 days remain.'
            ' Multiplied with the daily hours (5) and number of employees (2),'
            ' the result should be 21 * 5 * 2 = 210'))

    def test_get_available_ressources_max_per_person(self):
        fixtures.create_month(self)
        result = self.month.get_available_ressources_max_per_person()
        self.assertEqual(result, 105, msg=(
            'January has 22 work days. Minus holidays, 21 days remain.'
            ' Multiplied with the daily hours (5) the result should be'
            ' 21 * 5 = 105'))

    def test_get_average_rate(self):
        fixtures.create_project_months(self)
        result = self.month.get_average_rate()
        self.assertEqual(result, 100, msg=(
            'Should divide the total profit by the total cashflow hours'))

    def test_get_cashflow_projects(self):
        fixtures.create_project_months(self)
        result = self.month.get_cashflow_projects()
        self.assertEqual(result.count(), 1, msg=(
            'Should return all projects that have is_investment=False'))
        self.assertFalse(result[0].project.is_investment, msg=(
            'Should return all projects that have is_investment=False'))

    def test_get_date(self):
        fixtures.create_month(self)
        result = self.month.get_date()
        expected = datetime.date(2015, 1, 1)
        self.assertEqual(result, expected, msg=(
            'Should return a date object for this month'))

    def test_get_employees(self):
        fixtures.create_employee_project_months(self)
        result = self.month.get_employees()
        self.assertEqual(result.count(), 2, msg=(
            'Should return all employees that have projects in this month'))

    def test_get_investment_projects(self):
        fixtures.create_project_months(self)
        result = self.month.get_investment_projects()
        self.assertEqual(result.count(), 1, msg=(
            'Should return all projects that have is_investment=True'))
        self.assertTrue(result[0].project.is_investment, msg=(
            'Should return all projects that have is_investment=True'))

    def test_get_total_cashflow_hours(self):
        fixtures.create_project_months(self)
        result = self.month.get_total_cashflow_hours()
        self.assertEqual(result, 10, msg=(
            'Should add up all budget hours for each cashflow project (the'
            ' hours that can be spend on projects for the given budget and'
            ' rate)'))

    def test_get_total_investment_hours(self):
        fixtures.create_project_months(self)
        result = self.month.get_total_investment_hours()
        self.assertEqual(result, 20, msg=(
            'Should add up all budget hours for each investment project (the'
            ' hours that can be spend on projects for the given budget and'
            ' rate)'))

    def test_get_total_investment(self):
        fixtures.create_project_months(self)
        result = self.month.get_total_investment()
        self.assertEqual(result, 4000, msg=(
            'Should add up all budgets for all investment projects.'))

    def test_get_total_profit(self):
        fixtures.create_project_months(self)
        result = self.month.get_total_profit()
        self.assertEqual(result, 1000, msg=(
            'Should add up all budgets for all cashflow projects.'))

    def test_get_unused_hours(self):
        fixtures.create_project_months(self)
        result = self.month.get_unused_hours()
        self.assertEqual(result, 160, msg=(
            'Should add up all budget hours for all projects in this month,'
            ' then substract this from the total available ressources of this'
            ' month.'))

    def test_get_unused_daily_hours(self):
        fixtures.create_project_months(self)
        result = self.month.get_unused_daily_hours()
        self.assertEqual(result, 160.0 / 19, msg=(
            'Should take the total unused hours and divide them by the number'
            ' of work days in this month'))

    def test_get_unused_budget(self):
        fixtures.create_project_months(self)
        result = self.month.get_unused_budget()
        self.assertEqual(result, 160.0 * 100, msg=(
            'Should multiply the unused hours with the default rate for this'
            ' year.'))

    def test_get_weekdays(self):
        fixtures.create_month(self)
        result = self.month.get_weekdays()
        self.assertEqual(result, 22, msg=(
            'Should return 22 weekdays for January 2015'))

    def test_get_work_days(self):
        fixtures.create_month(self)
        result = self.month.get_work_days()
        self.assertEqual(result, 19, msg=(
            'January has 22 work days. Minus one public holiday. Minus 1'
            ' vacation day (12 / 12). Minus one sick leave day (12 / 12).'
            ' Therefore, the result should be 22 - 1 - 1 -1 = 19'))

        result = self.month.get_work_days(minus_sick_leave=False)
        self.assertEqual(result, 20, msg=(
            'Like above, but this time we do not substract the sick-leave'
            ' days'))

        result = self.month.get_work_days(
            minus_sick_leave=False, minus_vacations=False)
        self.assertEqual(result, 21, msg=(
            'Like above, but this time we do not substract the sick-leave'
            ' and vacation days'))

    def test_get_work_days_max(self):
        fixtures.create_month(self)
        result = self.month.get_work_days_max()
        self.assertEqual(result, 21, msg=(
            'January has 22 work days. Minus public holidays, the result'
            ' should be 21'))

    def test_get_workload(self):
        fixtures.create_employee_project_months(self)
        result = self.month.get_workloads()
        expected = self.project_month1_1.get_daily_hours()
        self.assertEqual(
            result[self.employee1.freckle_id]['cashflow_workload'], expected,
            msg=('When the employee has 100% responsibility for the project,'
                 ' the result should equal the daily hours for that project'
                 ' in this month'))

        expected = self.project_month1_2.get_daily_hours() * 0.5
        self.assertEqual(
            result[self.employee2.freckle_id]['investment_workload'], expected,
            msg=('When the employee has 50% responsibility for the project,'
                 ' the result should equal 50% of the daily hours for that'
                 ' project in this month'))


class ProjectManagerTestCase(TestCase):
    """Tests for the ``ProjectManager`` model manager."""
    longMessage = True

    def test_get_for_year(self):
        fixtures.create_project_months(self)
        mixer.blend(
            'freckle_budgets.Project', freckle_project_id='101')
        manager = models.Project.objects
        result = manager.get_for_year(2015)
        self.assertEqual(result.count(), 2, msg=(
            'Should return all projects that have ProjectMonth instances for'
            ' the given year'))


class ProjectTestCase(TestCase):
    """Tests for the ``Project`` model."""
    longMessage = True

    def test_model(self):
        obj = mixer.blend('freckle_budgets.Project')
        self.assertTrue(obj.pk, msg=('Object can be saved'))
        self.assertEqual(obj.__str__(), obj.name, msg=(
            '__str__ should return correct string'))


class ProjectMonthManagerTestCase(TestCase):
    """Tests for the ``ProjectManager` model manager."""
    longMessage = True

    def test_get_project_months(self):
        fixtures.create_project_months(self)
        mixer.blend('freckle_budgets.Month', month=2, year__year=2015)
        manager = models.ProjectMonth.objects
        result = manager.get_project_months(2015)
        self.assertEqual(result[0][0], self.month, msg=(
            'Should return a list of lists. The inner lists consist of a month'
            ' and a list of projects for this month.'))

    def test_get_freckle_projects(self):
        fixtures.create_project_months(self)
        manager = models.ProjectMonth.objects
        result = manager.get_freckle_projects(2015)
        self.assertEqual(list(result), [u'1', u'2'], msg=(
            'Should return all freckle project IDs for this month'))


class ProjectMonthTestCase(TestCase):
    """Tests for the ``ProjectMonth`` model."""
    longMessage = True

    def test_model(self):
        obj = mixer.blend('freckle_budgets.ProjectMonth')
        self.assertTrue(obj.pk, msg=('Object can be saved'))

        result = obj.__str__()
        expected = '{0} - {1}'.format(obj.project, obj.month)
        self.assertEqual(result, expected, msg=(
            '__str__ should return correct string'))

    def test_get_budget_hours(self):
        fixtures.create_project_months(self)

        result = self.project_month1_1.get_budget_hours()
        expected = self.project_month1_1.budget / self.project_month1_1.rate
        self.assertEqual(result, expected, msg=(
            'Should return the hours that can be worked on this project given'
            ' the budget and hourly rate'))

        self.project_month1_1.overhead_previous_month = \
            self.project_month1_1.budget / 2
        self.project_month1_1.save()
        expected = expected / 2
        result = self.project_month1_1.get_budget_hours()
        self.assertEqual(result, expected, msg=(
            'Should return the hours that can be worked on this project given'
            ' the budget and hourly rate, should deduct eventual overhead'
            ' hours from the budget when calculating the result'))

    def test_get_daily_hours(self):
        fixtures.create_project_months(self)
        pm = self.project_month1_1
        result = pm.get_daily_hours()
        expected = pm.get_budget_hours() / pm.month.get_work_days()
        self.assertEqual(result, expected, msg=(
            'Should return the daily hours that need to be worked on this'
            ' given the project budget, rate and work days of this month.'))


class EmployeeProjectMonthTestCase(TestCase):
    """Tests for the ``EmployeeProjectMonth`` model."""
    longMessage = True

    def test_model(self):
        obj = mixer.blend('freckle_budgets.EmployeeProjectMonth')
        self.assertTrue(obj.pk, msg=('Object can be saved'))

        expected = '{0} - {1}'.format(obj.project_month, obj.employee)
        self.assertEqual(obj.__str__(), expected, msg=(
            '__str__ should return correct string'))

    def test_get_budget_hours(self):
        fixtures.create_employee_project_months(self)
        result = self.employee_project_month.get_budget_hours()
        self.assertEqual(result, 10, msg=(
            'Should return the hours this employee should be working on this'
            ' project according to the project budget and his responsibility'))
