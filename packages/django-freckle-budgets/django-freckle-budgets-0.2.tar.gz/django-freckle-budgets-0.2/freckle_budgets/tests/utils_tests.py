"""Tests for the utilities of the freckle_budgets app."""
import datetime

from django.test import TestCase

from .. import utils


class GetWorkdayNumberTestCase(TestCase):
    """Tests for the ``get_workday_number`` function."""
    longMessage = True

    def test_function(self):
        jan1 = datetime.datetime(2015, 1, 1)
        result = utils.get_workday_number(jan1)
        self.assertEqual(result, 1, msg=(
            'January 1st 2015 is a workday, so it is the first workday of the'
            ' month.'))

        jan2 = datetime.datetime(2015, 1, 2)
        result = utils.get_workday_number(jan2)
        self.assertEqual(result, 2, msg=(
            'January 2nd 2015 is a workday as well, so it is the second'
            ' workday of the month.'))

        jan5 = datetime.datetime(2015, 1, 5)
        result = utils.get_workday_number(jan5)
        self.assertEqual(result, 3, msg=(
            'January 5th 2015 is a workday after a weekend, so it is the third'
            ' workday of the month.'))

        jan30 = datetime.datetime(2015, 1, 30)
        result = utils.get_workday_number(jan30)
        self.assertEqual(result, 22, msg=(
            'January 30th 2015 is the last workday of the month, so it is the'
            ' 22nd workday of the month.'))
