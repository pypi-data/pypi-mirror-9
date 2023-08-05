# -*- coding:utf-8 -*-
"""
urls
"""

from django.conf.urls import patterns, include, url

urlpatterns = patterns('coop_cms.apps.rss_sync.views',
    url(r'^collect-rss-items/(?P<source_id>\d+)$', 'collect_rss_items_view', name='rss_sync_collect_rss_items'),
    url(r'^create-cms-article/(?P<item_id>\d+)$', 'create_cms_article_view', name='rss_sync_create_cms_article'),
)
