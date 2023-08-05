"""Views for the freckle_budgets app."""
from django.conf import settings
from django.views.generic import TemplateView

from . import freckle_api
from . import models


class YearView(TemplateView):
    template_name = 'freckle_budgets/year_view.html'

    def get_context_data(self, **kwargs):
        year = kwargs.get('year')
        start_date = '{0}-01-01'.format(year)
        end_date = '{0}-12-31'.format(year)

        ctx = super(YearView, self).get_context_data(**kwargs)
        project_months = models.ProjectMonth.objects.get_project_months(year)
        api = freckle_api.FreckleClient(
            account_name=settings.FRECKLE_BUDGETS_ACCOUNT_NAME,
            api_token=settings.FRECKLE_BUDGETS_API_TOKEN)

        projects = models.Project.objects.get_for_year(year)
        entries = api.get_entries(projects, start_date, end_date)
        entries_times = freckle_api.get_project_times(projects, entries)

        ctx.update({
            'year': models.Year.objects.get(year=year),
            'project_months': project_months,
            'entries': entries,
            'entries_times': entries_times,
        })
        return ctx
