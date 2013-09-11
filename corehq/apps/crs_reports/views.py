from django.shortcuts import render
from django.views.decorators.http import require_GET
from corehq.apps.domain.decorators import login_and_domain_required
from corehq.apps.reports.views import require_case_view_permission


@require_case_view_permission
@login_and_domain_required
@require_GET
def case_details_report(request, domain, case_id):
     return render(request, 'crs_reports/mothers_form_reports_template.html', {
        "domain": domain,
        "case_id": case_id,
    })