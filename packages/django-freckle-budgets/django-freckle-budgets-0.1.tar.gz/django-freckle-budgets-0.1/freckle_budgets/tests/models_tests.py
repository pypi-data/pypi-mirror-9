"""Tests for the models of the freckle_budgets app."""
import datetime

from django.test import TestCase

from mixer.backend.django import mixer

from .. import models


def create_month(cls):
    cls.month = mixer.blend(
        'freckle_budgets.Month', month=1, year__year=2015,
        year__sick_leave_days=12, year__vacation_days=12, year__rate=100,
        public_holidays=1, employees=2)


def create_project_months(cls):
    """If needed, must be called after ``create_month()``"""
    cls.proj1 = mixer.blend(
        'freckle_budgets.Project', is_investment=False, freckle_project_id='1')
    cls.proj2 = mixer.blend(
        'freckle_budgets.Project', is_investment=True, freckle_project_id='2')
    cls.project_month1 = mixer.blend(
        'freckle_budgets.ProjectMonth', project=cls.proj1,
        month=cls.month, budget=1000, rate=100, )
    cls.project_month2 = mixer.blend(
        'freckle_budgets.ProjectMonth', project=cls.proj2,
        month=cls.month, budget=2000, rate=200, )


class YearTestCase(TestCase):
    """Tests for the ``Year`` model."""
    longMessage = True

    def test_model(self):
        obj = mixer.blend('freckle_budgets.Year')
        self.assertTrue(obj.pk, msg=('Object can be saved'))
        self.assertEqual(obj.__str__(), str(obj.year), msg=(
            '__str__ should return correct string'))


class MonthManagerTestCase(TestCase):
    """Tests for the ``MonthManager`` model manager."""
    longMessage = True

    def test_get_months_with_projects(self):
        create_month(self)
        create_project_months(self)
        mixer.blend('freckle_budgets.Month', month=2, year__year=2015)

        manager = models.Month.objects
        result = manager.get_months_with_projects(2015)
        self.assertEqual(result.count(), 1, msg=(
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
        create_month(self)
        result = self.month.get_available_ressources()
        self.assertEqual(result, 190, msg=(
            'January has 22 work days. Minus holidays, vacations and sick'
            ' leave, 19 days remain. Multiplied with the daily hours (5) and'
            ' number of employees (2), the result should be 19 * 5 * 2 = 190'))

    def test_get_cashflow_projects(self):
        create_month(self)
        create_project_months(self)
        result = self.month.get_cashflow_projects()
        self.assertEqual(result.count(), 1, msg=(
            'Should return all projects that have is_investment=False'))
        self.assertFalse(result[0].project.is_investment, msg=(
            'Should return all projects that have is_investment=False'))

    def test_get_date(self):
        create_month(self)
        result = self.month.get_date()
        expected = datetime.date(2015, 1, 1)
        self.assertEqual(result, expected, msg=(
            'Should return a date object for this month'))

    def test_get_investment_projects(self):
        create_month(self)
        create_project_months(self)
        result = self.month.get_investment_projects()
        self.assertEqual(result.count(), 1, msg=(
            'Should return all projects that have is_investment=True'))
        self.assertTrue(result[0].project.is_investment, msg=(
            'Should return all projects that have is_investment=True'))

    def test_get_total_cashflow_hours(self):
        create_month(self)
        create_project_months(self)
        result = self.month.get_total_cashflow_hours()
        self.assertEqual(result, 10, msg=(
            'Should add up all budget hours for each cashflow project (the'
            ' hours that can be spend on projects for the given budget and'
            ' rate)'))

    def test_get_total_investment_hours(self):
        create_month(self)
        create_project_months(self)
        result = self.month.get_total_investment_hours()
        self.assertEqual(result, 10, msg=(
            'Should add up all budget hours for each investment project (the'
            ' hours that can be spend on projects for the given budget and'
            ' rate)'))

    def test_get_total_investment(self):
        create_month(self)
        create_project_months(self)
        result = self.month.get_total_investment()
        self.assertEqual(result, 2000, msg=(
            'Should add up all budgets for all investment projects.'))

    def test_get_total_profit(self):
        create_month(self)
        create_project_months(self)
        result = self.month.get_total_profit()
        self.assertEqual(result, 1000, msg=(
            'Should add up all budgets for all cashflow projects.'))

    def test_get_unused_hours(self):
        create_month(self)
        create_project_months(self)
        result = self.month.get_unused_hours()
        self.assertEqual(result, 170, msg=(
            'Should add up all budget hours for all projects in this month,'
            ' then substract this from the total available ressources of this'
            ' month.'))

    def test_get_unused_daily_hours(self):
        create_month(self)
        create_project_months(self)
        result = self.month.get_unused_daily_hours()
        self.assertEqual(result, 170.0 / 19, msg=(
            'Should take the total unused hours and divide them by the number'
            ' of work days in this month'))

    def test_get_unused_budget(self):
        create_month(self)
        create_project_months(self)
        result = self.month.get_unused_budget()
        self.assertEqual(result, 170.0 * 100, msg=(
            'Should multiply the unused hours with the default rate for this'
            ' year.'))

    def test_get_weekdays(self):
        create_month(self)
        result = self.month.get_weekdays()
        self.assertEqual(result, 22, msg=(
            'Should return 22 weekdays for January 2015'))

    def test_get_work_days(self):
        create_month(self)
        result = self.month.get_work_days()
        self.assertEqual(result, 19, msg=(
            'January has 22 work days. Minus one public holiday. Minus 1'
            ' vacation day (12 / 12). Minus one sick leave day (12 / 12).'
            ' Therefore, the result should be 22 - 1 - 1 -1 = 19'))


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
        create_month(self)
        create_project_months(self)
        mixer.blend('freckle_budgets.Month', month=2, year__year=2015)
        manager = models.ProjectMonth.objects
        result = manager.get_project_months(2015)
        self.assertEqual(result[0][0], self.month, msg=(
            'Should return a list of lists. The inner lists consist of a month'
            ' and a list of projects for this month.'))

    def test_get_freckle_projects(self):
        create_month(self)
        create_project_months(self)
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
        create_month(self)
        create_project_months(self)
        result = self.project_month1.get_budget_hours()
        expected = self.project_month1.budget / self.project_month1.rate
        self.assertEqual(result, expected, msg=(
            'Should return the hours that can be worked on this project given'
            ' the budget and hourly rate'))

    def test_get_daily_hours(self):
        create_month(self)
        create_project_months(self)
        pm = self.project_month1
        result = pm.get_daily_hours()
        expected = pm.get_budget_hours() / pm.month.get_work_days()
        self.assertEqual(result, expected, msg=(
            'Should return the daily hours that need to be worked on this'
            ' given the project budget, rate and work days of this month.'))
