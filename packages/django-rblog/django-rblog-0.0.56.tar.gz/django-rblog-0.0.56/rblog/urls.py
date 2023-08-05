# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from django.contrib.sitemaps import views as sitemaps_views
from django.views.decorators.cache import cache_page

from rblog.feeds import AllFeed, TagFeed
from rblog.views import (BlogIndexView,
                         PostDetailView,
                         PostTempView,
                         PostsWithTag,
                         PostsByDate,
                         AJAXArchive,
                         BlogSitemap,
                         PostLinkAdd,
                         LinkblogIndexView,
                         )

sitemaps = {
    'blog': BlogSitemap,
}

ctime = (60 * 24 * 7)
urlpatterns = patterns(
    '',
    url(r'^$',
        BlogIndexView.as_view(),
        {},
        'app_blog-index'
        ),
    url(r'^linkblog/$',
        LinkblogIndexView.as_view(),
        {},
        'app_blog-linkblog'
        ),
    url(r'^page/(?P<page>\d+)/$',
        BlogIndexView.as_view(),
        {},
        'app_blog-index-page'
        ),
    url(r'^(?P<slug>[-\w]+)\.html$',
        PostDetailView.as_view(),
        {},
        'app_blog-post-detail'
        ),
    url(r'^(?P<slug>[-\w]+)\.tmp$',
        PostTempView.as_view(),
        {},
        'app_blog-post-detail-temp'
        ),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/$',
        PostsByDate.as_view(),
        {},
        'app_blog-archive'
        ),
    url(r'^(?P<year>\d{4})/(?P<month>\d{1,2})/page/(?P<page>\d+)/$',
        PostsByDate.as_view(),
        {},
        'app_blog-archive-page'
        ),
    url(r'^tag-(?P<tag>[-_A-Za-z0-9]+)/$',
        PostsWithTag.as_view(),
        {},
        'app_blog-with_tag'
        ),
    url(r'^tag-(?P<tag>[-_A-Za-z0-9]+)/page/(?P<page>\d+)/$',
        PostsWithTag.as_view(),
        {},
        'app_blog-with_tag_page'
        ),
    url(r'^tag-(?P<tag>[-_A-Za-z0-9]+)/feed/$',
        TagFeed(),
        {},
        'app_blog-tagfeed'
        ),
    url(r'^tag-(?P<tag>[-_A-Za-z0-9]+)/feed.rss$',
        TagFeed(),
        {},
        'app_blog-tagfeed2'
        ),
    url(r'^feed/$',
        AllFeed(),
        {},
        'app_blog-feed'
        ),
    url(r'^feed.rss$',
        AllFeed(),
        {},
        'app_blog-feed2'
        ),
    url(r'^post/link/add/$',
        PostLinkAdd.as_view(),
        name='app_blog-post-link-add'),
    # 7 days cache
    url(r'^ajax/testing/$',
        cache_page(ctime)(AJAXArchive.as_view()), {}, 'app_blog-ajaxarchive'),
    url(r'^archive/$',
        cache_page(ctime)(AJAXArchive.as_view()), {}, 'app_blog-archive'),

    # sitemap.xml
    url(r'^sitemap\.xml$',
        cache_page(ctime)(sitemaps_views.sitemap),
        {'sitemaps': sitemaps})

)
