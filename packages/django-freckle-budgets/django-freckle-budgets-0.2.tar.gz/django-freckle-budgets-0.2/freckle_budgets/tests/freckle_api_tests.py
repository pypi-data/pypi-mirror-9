"""Tests for the Freckle api client of the freckle_budgets app."""
from django.test import TestCase

from mock import MagicMock, patch

from . import fixtures
from .. import freckle_api
from .. import models


class FreckleClientTestCase(TestCase):
    """Tests for the ``FreckleClient`` class."""
    longMessage = True

    def test_fetch_json(self):
        client = freckle_api.FreckleClient('account_name', 'api_token')
        with patch('freckle_budgets.freckle_api.requests.request') as request_mock:  # NOQA
            request_mock.return_value = MagicMock()
            # Should raise an Exception if the response is not 200
            self.assertRaises(Exception, client.fetch_json, 'entries')

            request_mock.return_value.status_code = 200
            client.fetch_json('entries')
            self.assertEqual(request_mock.call_count, 2, msg=(
                'Should call the Freckle API via the requests module'))

    def test_get_entries(self):
        client = freckle_api.FreckleClient('account_name', 'api_token')
        with patch('freckle_budgets.freckle_api.requests.request') as request_mock:  # NOQA
            request_mock.return_value = MagicMock()
            request_mock.return_value.status_code = 200
            request_mock.return_value.json = MagicMock()
            request_mock.return_value.json.return_value = \
                fixtures.get_api_response(self)
            projects = models.Project.objects.get_for_year(self.year.year)
            client.get_entries(projects, '2015-01-01', '2015-01-10')
            self.assertEqual(request_mock.call_count, 1, msg=(
                'Should call the Freckle API via the requests module'))


class GetProjectTimesTestCase(TestCase):
    """Tests for the ``get_project_times`` function."""
    longMessage = True

    def test_function(self):
        entries = fixtures.get_api_response(self)
        projects = models.Project.objects.get_for_year(self.year.year)

        expected = {
            1: {
                111: {
                    1111: 5,
                    'total': 5,
                },
                222: {
                    2222: 8,
                    'total': 8,
                },
            },
            2: {
                222: {
                    2222: 16,
                    'total': 16,
                },
                333: {
                    1111: 32,
                    'total': 32,
                },
            },
        }

        result = freckle_api.get_project_times(projects, entries)
        self.assertEqual(result, expected, msg=(
            'Should turn the list of entries into a dict that has months as'
            ' keys and each month is a dict that has project IDs as keys and'
            ' the final values is the total minutes booked on that project'
            ' in that month.'))
