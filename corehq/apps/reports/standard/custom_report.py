from datetime import datetime
import json

from couchdbkit.exceptions import ResourceNotFound
from couchdbkit.resource import RequestFailed
import dateutil
from django.core.urlresolvers import reverse, NoReverseMatch
from django.template.defaultfilters import yesno
from django.utils import html
from django.utils.safestring import mark_safe
import pytz
from django.conf import settings
from django.core import cache
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_noop

from casexml.apps.case.models import CommCareCaseAction
from corehq.apps.reports.standard import ProjectReport, ProjectReportParametersMixin, DatespanMixin
from corehq.apps.reports.fields import StrongFilterUsersField, ReportSelectField
from corehq.apps.reports.generic import ElasticProjectInspectionReport
from corehq.apps.reports.standard.monitoring import MultiFormDrilldownMixin

class MotherHNBCReport(ElasticProjectInspectionReport, ProjectReport, ProjectReportParametersMixin, MultiFormDrilldownMixin, DatespanMixin):
    name = ugettext_noop('Mother HNBC Form')
    slug = 'hnbc_mother_report'
    fields = [
              'corehq.apps.reports.fields.SelectPNCStatusField',
              'corehq.apps.reports.standard.inspect.CaseSearchFilter',
              'corehq.apps.reports.fields.DatespanField']
    ajax_pagination = True
    filter_users_field_class = StrongFilterUsersField
    include_inactive = True


class InfantHNBCReport(ElasticProjectInspectionReport, ProjectReport, ProjectReportParametersMixin, MultiFormDrilldownMixin, DatespanMixin):
    name = ugettext_noop('Infant HNBC Form')
    slug = 'hnbc_infant_report'
    fields = [
              'corehq.apps.reports.fields.SelectPNCStatusField',
              'corehq.apps.reports.standard.inspect.CaseSearchFilter',
              'corehq.apps.reports.fields.DatespanField']
    ajax_pagination = True
    filter_users_field_class = StrongFilterUsersField
    include_inactive = True

