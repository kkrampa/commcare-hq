from django.conf.urls.defaults import *

urlpatterns = patterns('corehq.apps.crs_reports.views',
    url(r'^(?P<case_id>[\w\-]+)', "case_details_report", name="case_details_report"),
)