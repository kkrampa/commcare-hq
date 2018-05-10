# encoding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals
import calendar
import datetime
import json
from django.urls import reverse
from django.utils.translation import ugettext_noop
from corehq.apps.locations.util import location_hierarchy_config, load_locs_json
from corehq.apps.reports.filters.base import BaseReportFilter
from corehq.apps.reports.filters.fixtures import AsyncLocationFilter
from corehq.apps.reports.filters.select import YearFilter, MonthFilter
from corehq.util.translation import localize
from django.utils.translation import ugettext as _
from six.moves import range
from six.moves import filter

from custom.intrahealth.sqldata import ProgramData


class LocationFilter(AsyncLocationFilter):
    label = ugettext_noop("Region")
    slug = "ih_location_async"
    template = 'intrahealth/location_filter.html'
    required = 0

    @property
    def ctx(self):
        api_root = reverse('api_dispatch_list', kwargs={'domain': self.domain,
                                                        'resource_name': 'location_internal',
                                                        'api_name': 'v0.5'})
        selected_loc_id = self.request.GET.get('location_id')

        locations = load_locs_json(self.domain, selected_loc_id)

        if self.required != 2:
            f = lambda y: 'children' in y
            districts = list(filter(f, locations))
            if districts:
                PPS = list(filter(f, districts[0]['children']))
                if PPS:
                    del PPS[0]['children']
        return {
            'api_root': api_root,
            'control_name': self.label,
            'control_slug': self.slug,
            'loc_id': selected_loc_id,
            'locations': json.dumps(locations),
            'hierarchy': [loc for loc in location_hierarchy_config(self.domain) if loc[0] != 'PPS'],
        }

    @property
    def filter_context(self):
        context = self.ctx
        context.update(dict(required=self.required))
        return context


class FicheLocationFilter(LocationFilter):
    required = 1


class RecapPassageLocationFilter(LocationFilter):
    required = 2

    @property
    def filter_context(self):
        context = super(RecapPassageLocationFilter, self).filter_context
        context.update(dict(hierarchy=location_hierarchy_config(self.domain)))
        return context


class FRYearFilter(YearFilter):
    label = ugettext_noop("Année")


class FRMonthFilter(MonthFilter):
    label = ugettext_noop("Mois")

    @property
    def options(self):
        with localize('fr'):
            return [("%02d" % m, _(calendar.month_name[m])) for m in range(1, 13)]


class YeksiNaaLocationFilter(AsyncLocationFilter):
    label = ugettext_noop("Location")
    slug = "yeksi_naa_location_async"
    template = 'yeksi_naa/location_filter.html'

    @property
    def filter_context(self):
        api_root = reverse('api_dispatch_list', kwargs={'domain': self.domain,
                                                        'resource_name': 'location_internal',
                                                        'api_name': 'v0.5'})
        selected_loc_id = self.request.GET.get('location_id')
        locations = load_locs_json(self.domain, selected_loc_id)

        return {
            'api_root': api_root,
            'control_name': self.label,
            'control_slug': self.slug,
            'loc_id': selected_loc_id if selected_loc_id else '',
            'locations': json.dumps(locations),
            'hierarchy': [loc for loc in location_hierarchy_config(self.domain)],
        }


class MonthsDateFilter(BaseReportFilter):
    template = "yeksi_naa/months_datespan.html"
    slug = 'datespan'
    label = "Plage de dates"

    @classmethod
    def months(cls):
        return [
            {'name': 'Janvier', 'value': 1}, {'name': 'Février', 'value': 2},
            {'name': 'Mars', 'value': 3}, {'name': 'Avril', 'value': 4},
            {'name': 'Mai', 'value': 5}, {'name': 'Juin', 'value': 6},
            {'name': 'Juillet', 'value': 7}, {'name': 'Août', 'value': 8},
            {'name': 'Septembre', 'value': 9}, {'name': 'Octobre', 'value': 10},
            {'name': 'Novembre', 'value': 11}, {'name': 'Décembre', 'value': 12}
        ]

    @property
    def filter_context(self):
        oldest_year = 2016
        return {
            'months': self.months(),
            'years': list(range(oldest_year, datetime.date.today().year + 1)),
            'starting_month': int(self.request.GET.get('month_start', 1)),
            'starting_year': int(self.request.GET.get('year_start', datetime.date.today().year)),
            'current_month': int(self.request.GET.get('month_end', datetime.date.today().month)),
            'current_year': int(self.request.GET.get('year_end', datetime.date.today().year)),
        }


class ProgramFilter(BaseReportFilter):
    template = "yeksi_naa/program_filter.html"
    slug = 'program'
    label = "Programme"

    def program(self):
        program_filter = [{
            'name': 'All',
            'value': "",
        }]
        programs = ProgramData(config={'domain': self.domain}).rows
        for program in programs:
            program_filter.append({
                'name': program[1],
                'value': "%{0}%".format(program[0]),
            })
        return program_filter

    @property
    def filter_context(self):
        return {
            'programs': self.program(),
            'chosen_program': self.request.GET.get('program', ''),
        }
