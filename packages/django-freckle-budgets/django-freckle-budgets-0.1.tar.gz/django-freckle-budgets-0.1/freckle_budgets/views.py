"""Views for the freckle_budgets app."""
from django.conf import settings
from django.views.generic import TemplateView

from . import freckle_api
from . import models


class YearView(TemplateView):
    template_name = 'freckle_budgets/year_view.html'

    def get_context_data(self, **kwargs):
        ctx = super(YearView, self).get_context_data(**kwargs)
        project_months = models.ProjectMonth.objects.get_project_months(2015)
        api = freckle_api.FreckleClient(
            account_name=settings.FRECKLE_BUDGETS_ACCOUNT_NAME,
            api_token=settings.FRECKLE_BUDGETS_API_TOKEN)

        freckle_projects = models.ProjectMonth.objects.get_freckle_projects(
            2015)
        entries = api.get_entries(freckle_projects, '2015-01-01', '2015-12-31')
        entries_times = freckle_api.get_project_times(entries)

        ctx.update({
            'year': models.Year.objects.get(year=2015),
            'project_months': project_months,
            'entries': entries,
            'entries_times': entries_times,
        })
        return ctx
