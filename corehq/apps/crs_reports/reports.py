from corehq.apps.reports.standard import ProjectReportParametersMixin, DatespanMixin, CustomProjectReport
from corehq.apps.reports.generic import GenericTabularReport

class HNBCMotherReport(GenericTabularReport, CustomProjectReport,
                            ProjectReportParametersMixin, DatespanMixin):
    name = "HNBC Mother"
    slug = "hnbc_mother"

    fields = [
        'corehq.apps.reports.fields.FilterUsersField',
        'corehq.apps.reports.fields.DatespanField',
        'hsph.fields.DCTLToFIDAFilter',
    ]


class HNBCBabyReport(GenericTabularReport, CustomProjectReport,
                            ProjectReportParametersMixin, DatespanMixin):
    fields = []