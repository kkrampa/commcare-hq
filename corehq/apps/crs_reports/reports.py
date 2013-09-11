from django.utils.translation import ugettext_noop

from corehq.apps.reports.standard import CustomProjectReport, DatespanMixin
from corehq.apps.reports.fields import StrongFilterUsersField
from corehq.apps.reports.datatables import DataTablesHeader, DataTablesColumn
from corehq.apps.reports.standard.inspect import CaseDisplay, CaseListReport
from django.utils import html
from django.core.urlresolvers import reverse, NoReverseMatch

import pytz
from django.utils.translation import ugettext as _

from dimagi.utils.decorators.memoized import memoized
from dimagi.utils.timezones import utils as tz_utils


class HNBCReportDisplay(CaseDisplay):

    @property
    def dob(self):
        return "" #self.parse_date(self.case['dob'])

    @property
    def visit_completion(self):
        return "" #self.parse_date(self.case['visit_completion'])

    @property
    def delivery(self):
        return "" #self.parse_date(self.case['delivery'])

    @property
    def pnc_status(self):
        return "" #self.parse_date(self.case['pnc_status'])

    @property
    def case_link(self):
        case_id, case_name = self.case['_id'], self.case['name']
        try:
            return html.mark_safe("<a class='ajax_dialog' href='%s'>%s</a>" % (
                html.escape(reverse('case_details_report', args=[self.report.domain, case_id])),
                html.escape(case_name),
            ))
        except NoReverseMatch:
            return "%s (bad ID format)" % case_name


class BaseHNBCReport(CustomProjectReport, DatespanMixin, CaseListReport):

    fields = ['corehq.apps.reports.fields.SelectBlockField',
              'corehq.apps.reports.fields.SelectSubCenterField',
              'corehq.apps.reports.fields.SelectASHAField',
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
            DataTablesColumn(_("DOB"), prop_name="dob"),
            DataTablesColumn(_("PNC Visit Completion"), prop_name="visit_completion"),
            DataTablesColumn(_("Delivery"), prop_name="delivery"),
            DataTablesColumn(_("Case/PNC Status"), prop_name="pnc_status")
        )
        return headers

    @property
    def rows(self):
        case_displays = (HNBCReportDisplay(self, self.get_case(case))
                         for case in self.es_results['hits'].get('hits', []))

        for disp in case_displays:
            yield [
                disp.case_type,
                disp.case_link,
                disp.owner_display,
                disp.dob,
                disp.visit_completion,
                disp.delivery,
                disp.pnc_status,
            ]

    # @property
    # def case_filter(self):
    #     filters = [{
    #         'range': {
    #             'opened_on': {
    #                 "from": self.datespan.startdate_param_utc,
    #                 "to": self.datespan.enddate_param_utc
    #             }
    #         }
    #     }]
    #     return filters

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

    default_case_type = 'mother'

    @property
    def user_filter(self):
        return super(HNBCMotherReport, self).user_filter


class HNBCInfantReport(BaseHNBCReport):
    name = ugettext_noop('Infant HNBC Form')
    slug = 'hnbc_infant_report'

    default_case_type = 'baby'

    @property
    def user_filter(self):
        return super(HNBCInfantReport, self).user_filter

