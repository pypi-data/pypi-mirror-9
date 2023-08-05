"""Tests for the templatetags of the freckle_budgets app."""
import calendar
import datetime

from django.test import TestCase

from mixer.backend.django import mixer

from ..templatetags import freckle_budgets_tags as tags


class GetWeeksTestCase(TestCase):
    """Tests for the ``get_weeks`` assignment tag."""
    longMessage = True

    def test_tag(self):
        month = mixer.blend('freckle_budgets.Month', year__year=2015, month=1)
        expected = calendar.Calendar(0).monthdatescalendar(2015, 1)
        result = tags.get_weeks(month)
        self.assertEqual(result, expected, msg=(
            'Should return a list of weeks. Each list is a list of days'))


class IsBudgetFulfilledTestCase(TestCase):
    """Tests for the ``is_budget_fulfilled`` assignment tag."""
    longMessage = True

    def test_tag(self):
        project_month = mixer.blend(
            'freckle_budgets.ProjectMonth', budget=1000, rate=100)
        entries_times = {
            1: {101: 5, 102: 8, },
            2: {102: 16}
        }
        day = datetime.date(2015, 01, 01)

        result = tags.is_budget_fulfilled(entries_times, project_month, day)
        self.assertFalse(result, msg=(
            'Should return false when the project ID cannot be found in the'
            ' entries_times dict'))

        project_month = mixer.blend(
            'freckle_budgets.ProjectMonth',
            budget=1000, rate=100, project__freckle_project_id=101,
            month__public_holidays=0, month__year__year=2015, month__month=1,
            month__year__work_hours_per_day=5, month__year__sick_leave_days=0,
            month__year__vacation_days=0)

        result = tags.is_budget_fulfilled(entries_times, project_month, day)
        self.assertFalse(result, msg=(
            'This project needs 0.45hrs per day but we have only fulfilled'
            ' 5 minutes so far, so no day has been fulfilled, yet'))

        day = datetime.date(2015, 1, 5)
        entries_times[1][101] = 82
        result = tags.is_budget_fulfilled(entries_times, project_month, day)
        self.assertTrue(result, msg=(
            'This project needs 0.45hrs per day (27.27 minutes) and we have'
            ' fulfilled 82 minutes so far, so three days have been fulfilled,'
            ' already'))

        day = datetime.date(2015, 1, 6)
        result = tags.is_budget_fulfilled(entries_times, project_month, day)
        self.assertFalse(result, msg=(
            'Sanity check for the test above. If three days are fulfilled,'
            ' the fourth workday should not be fulfilled'))
