# -*- coding: utf-8 -*-
"""Define mappings from the URL requested by a user to a proper Python view."""
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from updoc.views import RssFeed, MostViewedFeed, LastDocsFeed

__author__ = "flanker"

admin.autodiscover()


urlpatterns = patterns(  # pylint: disable=C0103
    '',
    url(r'^admin/', include(admin.site.urls)),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog',
     {'packages': ('updoc', 'django.contrib.admin', ), }),
    (r'^' + settings.MEDIA_URL[1:] + '(?P<path>.*)$', 'updoc.views.static_serve',
     {'document_root': settings.MEDIA_ROOT}),
    (r'^' + settings.STATIC_URL[1:] + '(?P<path>.*)$', 'updoc.views.static_serve',
     {'document_root': settings.STATIC_ROOT}),
    url(r'^updoc/', include('updoc.urls')),
    url(r'^rss/favorites/(?P<root_id>\d+)/', RssFeed(), name='favorites'),
    url(r'^rss/most_viewed/', MostViewedFeed(), name='most_viewed_feed'),
    url(r'^rss/last_docs/', LastDocsFeed(), name='last_docs_rss'),
    url(r'^upload/$', 'updoc.views.upload'),
    url(r'^login/$', 'django.contrib.auth.views.login', kwargs={'template_name': 'login.html'}),
    url(r'^upload_doc/$', 'updoc.views.upload_doc'),
    url(r'^$', 'updoc.views.index'),
)
