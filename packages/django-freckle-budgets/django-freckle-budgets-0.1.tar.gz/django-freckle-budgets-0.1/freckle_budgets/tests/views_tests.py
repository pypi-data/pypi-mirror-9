"""Tests for the views of the freckle_budgets app."""
from django.test import RequestFactory, TestCase

from mixer.backend.django import mixer

from .. import views


class YearViewTestCase(TestCase):
    """Tests for the ``YearView`` view."""
    longMessage = True

    def test_view(self):
        mixer.blend('freckle_budgets.Year', year=2015)
        req = RequestFactory().get('/')
        resp = views.YearView.as_view()(req)
        self.assertEqual(resp.status_code, 200, msg=('View is callable'))
