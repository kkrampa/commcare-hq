from django.utils.translation import ugettext_noop

from corehq.apps.reports.standard import ProjectReport, ProjectReportParametersMixin, DatespanMixin
from corehq.apps.reports.fields import StrongFilterUsersField, ReportSelectField
from corehq.apps.reports.generic import ElasticProjectInspectionReport
from corehq.apps.reports.standard.monitoring import MultiFormDrilldownMixin

class HNBCMotherReport(ElasticProjectInspectionReport, ProjectReport, ProjectReportParametersMixin, MultiFormDrilldownMixin, DatespanMixin):
    name = ugettext_noop('Mother HNBC Form')
    slug = 'hnbc_mother_report'
    fields = [
              'corehq.apps.reports.fields.SelectPNCStatusField',
              'corehq.apps.reports.standard.inspect.CaseSearchFilter',
              'corehq.apps.reports.fields.DatespanField']
    ajax_pagination = True
    filter_users_field_class = StrongFilterUsersField
    include_inactive = True


class HNBCInfantReport(ElasticProjectInspectionReport, ProjectReport, ProjectReportParametersMixin, MultiFormDrilldownMixin, DatespanMixin):
    name = ugettext_noop('Infant HNBC Form')
    slug = 'hnbc_infant_report'
    fields = [
              'corehq.apps.reports.fields.SelectPNCStatusField',
              'corehq.apps.reports.standard.inspect.CaseSearchFilter',
              'corehq.apps.reports.fields.DatespanField']
    ajax_pagination = True
    filter_users_field_class = StrongFilterUsersField
    include_inactive = True