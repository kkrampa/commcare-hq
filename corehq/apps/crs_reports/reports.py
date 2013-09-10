from django.utils.translation import ugettext_noop

from corehq.apps.reports.standard import ProjectReport, ProjectReportParametersMixin, DatespanMixin
from corehq.apps.reports.fields import StrongFilterUsersField, ReportSelectField
from corehq.apps.reports.datatables import DataTablesHeader, DataTablesColumn
from corehq.apps.reports.generic import ElasticProjectInspectionReport
from corehq.apps.reports.standard.monitoring import MultiFormDrilldownMixin

import pytz
from django.utils.translation import ugettext as _

from dimagi.utils.decorators.memoized import memoized
from dimagi.utils.timezones import utils as tz_utils

class BaseHNBCReport(ElasticProjectInspectionReport, ProjectReport, ProjectReportParametersMixin, MultiFormDrilldownMixin, DatespanMixin):
    fields = [
              'corehq.apps.reports.fields.SelectPNCStatusField',
              'corehq.apps.reports.standard.inspect.CaseSearchFilter',
              'corehq.apps.reports.fields.DatespanField']
    ajax_pagination = True
    filter_users_field_class = StrongFilterUsersField
    include_inactive = True

    @property
    def headers(self):
        headers = DataTablesHeader(
            DataTablesColumn(_("Case Type"), prop_name="type.exact"),
            DataTablesColumn(_("Case Name"), prop_name="name.exact"),
            DataTablesColumn(_("CHW Name"), prop_name="owner_display", sortable=False),
            DataTablesColumn(_("DOB")),
            DataTablesColumn(_("PNC Visit Competion")),
            DataTablesColumn(_("Delivery")),
            DataTablesColumn(_("Case/PNC Status"))
        )
        return headers

    @property
    @memoized
    def rendered_report_title(self):
        if not self.individual:
            self.name = _("%(report_name)s for (0-42 days after delivery)") % {
                "report_name": _(self.name)
            }
        return self.name

    def date_to_json(self, date):
        return tz_utils.adjust_datetime_to_timezone\
            (date, pytz.utc.zone, self.timezone.zone).strftime\
            ('%Y-%m-%d') if date else ""


class HNBCMotherReport(BaseHNBCReport):
    name = ugettext_noop('Mother HNBC Form')
    slug = 'hnbc_mother_report'

    @property
    def user_filter(self):
        return super(HNBCMotherReport, self).user_filter


class HNBCInfantReport(BaseHNBCReport):
    name = ugettext_noop('Infant HNBC Form')
    slug = 'hnbc_infant_report'

    @property
    def user_filter(self):
        return super(HNBCInfantReport, self).user_filter

