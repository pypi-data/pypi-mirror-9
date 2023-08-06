# Django imports
from django.conf.urls import patterns, include, url


from djhcup_reporting.views import Index, QueryBuilder, DatasetDetails, DownloadArchive, UniverseDetails, BrowseDatasets


# base patterns always available through having djhcup_core installed
urlpatterns = patterns('',
    url(r'new/$', QueryBuilder.as_view(), name='query_builder'),
    url(r'universe/(?P<universe_pk>\d+)/$', UniverseDetails.as_view(), name='universe_details'),
    url(r'datasets/$', BrowseDatasets.as_view(), name='datasets_browse'),
    url(r'datasets/(?P<dataset_dbo_name>[_a-z0-9]+)/download/$', DownloadArchive.as_view(), name='download_archive'),
    url(r'datasets/(?P<dataset_dbo_name>[_a-z0-9]+)/$', DatasetDetails.as_view(), name='dataset_details'),
    url(r'$', Index.as_view(), name='djhcup_reporting|index')
)