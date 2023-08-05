"""
Helper method to fetch data from the Freckle API.

See http://developer.letsfreckle.com

"""
import datetime
import json

import requests


class FreckleClient(object):
    """Base class for Freckle API access."""
    def __init__(self, account_name, api_token):
        self.account_name = account_name
        self.api_token = api_token

    def fetch_json(self, uri_path, http_method='GET', headers=None,
                   query_params=None, post_args=None):
        """Fetch some JSON from Trello."""
        # explicit values here to avoid mutable default values
        if headers is None:
            headers = {}
        if query_params is None:
            query_params = {}
        if post_args is None:
            post_args = {}

        # set content type and accept headers to handle JSON
        headers['Accept'] = 'application/json'
        query_params['token'] = self.api_token

        # construct the full URL without query parameters
        url = 'https://{0}.letsfreckle.com/api/{1}.json'.format(
            self.account_name, uri_path)

        # perform the HTTP requests, if possible uses OAuth authentication
        response = requests.request(
            http_method, url, params=query_params, headers=headers,
            data=json.dumps(post_args))

        if response.status_code != 200:
            raise Exception(
                "Freckle API Response is not 200: %s" % (response.text))

        return response.json()

    def get_entries(self, projects, start_date, end_date):
        """
        Returns the entries for the given project and time frame.

        :param start_date: String representing the start date (YYYY-MM-DD).
        :param end_date: String representing the end date (YYYY-MM-DD).

        """
        entries = self.fetch_json(
            'entries',
            query_params={
                'per_page': 1000,
                'search[from]': start_date,
                'search[to]': end_date,
                'search[projects]': ','.join(projects),
            }
        )
        return entries


def get_project_times(entries):
    result = {}
    for entry in entries:
        entry_date = datetime.datetime.strptime(entry['entry']['date'], '%Y-%m-%d')
        if entry_date.month not in result:
            result[entry_date.month] = {}
        project_id = entry['entry']['project_id']
        if project_id not in result[entry_date.month]:
            result[entry_date.month][project_id] = 0
        if entry['entry']['billable']:
            result[entry_date.month][project_id] += entry['entry']['minutes']
    return result
