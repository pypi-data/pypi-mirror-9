"""Tests for the Freckle api client of the freckle_budgets app."""
from django.test import TestCase

from mock import MagicMock, patch

from .. import freckle_api


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
            client.get_entries(['proj1'], '2015-01-01', '2015-01-10')
            self.assertEqual(request_mock.call_count, 1, msg=(
                'Should call the Freckle API via the requests module'))


class GetProjectTimesTestCase(TestCase):
    """Tests for the ``get_project_times`` function."""
    longMessage = True

    def test_function(self):
        entries = [
            {
                # First project, first month, billable hours
                'entry': {
                    'date': '2015-01-01',
                    'project_id': 'proj1',
                    'billable': True,
                    'minutes': 1,
                }
            },
            {
                # Unbillable hours should not be added up
                'entry': {
                    'date': '2015-01-01',
                    'project_id': 'proj1',
                    'billable': False,
                    'minutes': 2,
                }
            },
            {
                # Billable hours should be added up
                'entry': {
                    'date': '2015-01-02',
                    'project_id': 'proj1',
                    'billable': True,
                    'minutes': 4,
                }
            },
            {
                # Another project in the same month
                'entry': {
                    'date': '2015-01-02',
                    'project_id': 'proj2',
                    'billable': True,
                    'minutes': 8,
                }
            },
            {
                # Another month
                'entry': {
                    'date': '2015-02-01',
                    'project_id': 'proj2',
                    'billable': True,
                    'minutes': 16,
                }
            },
        ]

        expected = {
            1: {'proj1': 5, 'proj2': 8, },
            2: {'proj2': 16}
        }

        result = freckle_api.get_project_times(entries)
        self.assertEqual(result, expected, msg=(
            'Should turn the list of entries into a dict that has months as'
            ' keys and each month is a dict that has project IDs as keys and'
            ' the final values is the total minutes booked on that project'
            ' in that month.'))
