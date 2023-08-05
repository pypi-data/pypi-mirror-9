from django.conf.urls import patterns
from django.conf.urls import url


urlpatterns = patterns(
    "crm.group.views",
    url(r"show/(?P<gid>\d+)/$", "group.show", name="show"),
    url(r"timetable/(?P<season>\d{4}\-\d{4})/(?P<typeid>\d+)/$", "group.timetable", name="timetable"),
    url(r"timetable/(?P<season>\d{4}\-\d{4})/$", "group.timetable"),
    url(r"timetable/current-season/$", "group.timetable", name="timetable-current-season"),
    url(r"timetable/next-season/$", "group.timetable_next_season", name="timetable-next-season"),
    url(r"table/(?P<season>\d{4}\-\d{4})/$", "group.timetable"),
    url(r"json/group/(?P<gid>\d+)/$", "json.group"),
    url(r"json/cost/(?P<gid>\d+)/$", "json.cost"),
    url(r"json/get_group_by_uid/(?P<uid>\d+)/$", "json.get_group_by_uid"),
    url(r"json/document/(?P<gid>\d+)/$", "json.document"),
)
