from __future__ import absolute_import

from django.conf.urls import patterns, url, include

from .views import (Search, PageDetailView,
                    PageListView, RootPageDetailView)

urlpatterns = patterns('',
    url(regex=r'^$',
        view=RootPageDetailView.as_view(),
        name='root'),
    url(regex=r'^search/$',
        view=Search.as_view(),
        name='search'),
    url(regex=r'^site_map/$',
        view=PageListView.as_view(),
        name='site_map'),
    url(regex=r'^dmcm/edit/',
        view=include('dmcm.edit.urls', namespace='edit')),
    url(regex=r'^(?P<slug>[-\w]+).html$',
        view=PageDetailView.as_view(),
        name='page_detail_html'),
    url(regex=r'^(?P<slug>[-\w]+)/$',
        view=PageDetailView.as_view(),
        name='page_detail'),
)
