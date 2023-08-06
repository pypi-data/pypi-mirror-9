# Django imports
from django.conf.urls import patterns, include, url

import views

# base patterns always available through having djhcup_core installed
ds_patterns = patterns('',
    url(r'(?P<obj_id>\d+)/$', views.ObjectDetail.as_view(), {'obj_type': 'DataSource'}, name='ds_detail'),
    url(r'$', views.ObjectInventory.as_view(), {'obj_type': 'DataSource'}, name='ds_inv'),
)

file_patterns = patterns('',
    url(r'(?P<obj_id>\d+)/$', views.ObjectDetail.as_view(), {'obj_type': 'File'}, name='file_detail'),
    url(r'(?P<year>\d+|all)/(?P<state_abbr>[A-Z]{2}|all)/$', views.ObjectInventory.as_view(), {'obj_type': 'File'}, name='file_inv'),
    url(r'discover/$', views.DiscoverFiles.as_view(), name='file_discover'),
    url(r'match/$', views.MatchFiles.as_view(), name='file_match'),
    url(r'$', views.ObjectInventory.as_view(), {'obj_type': 'File'}, name='file_inv'),
)

ibatch_patterns = patterns('',
    url(r'(?P<obj_id>\d+)/$', views.ObjectDetail.as_view(), {'obj_type': 'ImportBatch'}, name='imb_detail'),
    url(r'(?P<obj_id>\d+)/run/$', views.RunBatch.as_view(), {'obj_type': 'ImportBatch'}, name='imb_run'),
    url(r'unimported_batch/$', views.CreateUnimportedBatch.as_view(), name='imb_unimported'),
    url(r'$', views.ObjectInventory.as_view(), {'obj_type': 'ImportBatch'}, name='imb_inv'),
)

stbatch_patterns = patterns('',
    url(r'(?P<obj_id>\d+)/$', views.ObjectDetail.as_view(), {'obj_type': 'StagingBatch'}, name='stb_detail'),
    url(r'(?P<obj_id>\d+)/run/$', views.RunBatch.as_view(), {'obj_type': 'StagingBatch'}, name='stb_run'),
    url(r'unprocessed_batch/$', views.CreateUnprocessedBatch.as_view(), name='stb_unprocessed'),
    url(r'$', views.ObjectInventory.as_view(), {'obj_type': 'StagingBatch'}, name='stb_inv'),
)

tbl_patterns = patterns('',
    url(r'(?P<obj_id>\d+)/$', views.ObjectDetail.as_view(), {'obj_type': 'StagingTable'}, name='tbl_detail'),
    url(r'(?P<year>[0-9]{4}|all|None)/(?P<state_abbr>[A-Z]{2}|all|None)/$',
        views.ObjectInventory.as_view(),
        {'obj_type': 'StagingTable'},
        name='tbl_inv_filtered'
    ),
    url(r'$', views.ObjectInventory.as_view(), {'obj_type': 'StagingTable'}, name='tbl_inv'),
)

col_patterns = patterns('',
    url(r'(?P<obj_id>\d+)/$', views.ObjectDetail.as_view(), {'obj_type': 'Column'}, name='col_detail'), # links to the state-year and table each is from
    url(r'name/(?P<name>\S+)/$', views.ObjectInventory.as_view(), {'obj_type': 'Column'}, name='col_inv'), # shows the state-year and table each is from
)


urlpatterns = patterns('',
    url(r'data_sources/', include(ds_patterns)),
    url(r'files/', include(file_patterns)),
    url(r'imports/', include(ibatch_patterns)),
    url(r'staging/', include(stbatch_patterns)),
    url(r'tables/', include(tbl_patterns)),
    url(r'columns/', include(col_patterns)),
    url(r'^admin-tools/$', views.Admin.as_view(), name='djhcup_staging|admin'),
    url(r'^reset-dead/$', views.ResetDeadBatches.as_view(), name='reset_dead'),
    url(r'$', views.Index.as_view(), name='djhcup_staging|index')
)
