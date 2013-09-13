from couchdbkit.exceptions import ResourceNotFound
from casexml.apps.case.models import CommCareCase
from django.shortcuts import render
from django.views.decorators.http import require_GET
from corehq.apps.domain.decorators import login_and_domain_required
from corehq.apps.reports.views import require_case_view_permission
from casexml.apps.case.templatetags.case_tags import case_inline_display
from corehq.apps.app_manager.models import get_app
from corehq.apps.groups.models import Group
from corehq.apps.users.models import CommCareUser
import re



@require_case_view_permission
@login_and_domain_required
@require_GET
def case_details_report(request, domain, case_id, module_name, report_template, report_slug):

    try:
        case = CommCareCase.get(case_id)
    except ResourceNotFound:
        case = None

    try:
        owner_name = CommCareUser.get_by_user_id(case.owner_id, domain).raw_username
    except Exception:
        try:
            owning_group = Group.get(case.owner_id)
            owner_name = owning_group.display_name if owning_group.domain == domain else ''
        except Exception:
            owner_name = None

    try:
        username = CommCareUser.get_by_user_id(case.user_id, domain).raw_username
    except Exception:
        username = None

    questions = get_questions_with_answers(case.get_forms(), domain, case)

    return render(request, "%s/%s.html" % (module_name, report_template), {
        "domain": domain,
        "case_id": case_id,
        "report": dict(
            name=case_inline_display(case),
            slug=report_slug,
            is_async=False,
        ),
        "owner_name": owner_name,
        "username": username,
        "case": case,
        "questions": questions
    })


def get_questions_with_answers(forms, domain, case):
    questions_with_answers = []
    app = get_app(domain, getattr(forms[0], "app_id", None))
    for form in forms:
        questions = app.get_questions(form.xmlns)
        for question in questions:
            question_with_answers = {'question': question['label'],
                                     'answers': []}
            answer_field = re.search('.*/(.*)', question['value']).group(1)
    return questions_with_answers

