"""URLs for the freckle_budgets app."""
from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'^$', views.YearView.as_view(), name='freckle_budgets_year_view'),
)
