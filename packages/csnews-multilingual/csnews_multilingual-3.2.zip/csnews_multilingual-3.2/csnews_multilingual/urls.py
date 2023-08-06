from django.conf.urls import patterns, url, include

from csnews_multilingual.feeds import LatestNews
#feed_dict = {'rss': LatestNews}

urlpatterns = patterns('',
    (r'^$','csnews_multilingual.views.index'),
    url(r'^feed/$', LatestNews(),name='csnews_feed'),
    url(r'^hemeroteka/', 'csnews_multilingual.views.hemeroteka',name='csnews_archive'),
    url(r'^(?P<article_slug>[\-\d\w]+)/$','csnews_multilingual.views.article_index',name='csnews_article'),
)

