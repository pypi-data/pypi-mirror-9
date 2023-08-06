from django.conf.urls import patterns, url, include

from csnews_multilingual.feeds import LatestNews
#feed_dict = {'rss': LatestNews}

urlpatterns = patterns('',
    (r'^$','csnews_multilingual.views.index'),
    (r'^feed-(?P<url>.*)/$', LatestNews()),
    (r'^hemeroteka/', 'csnews_multilingual.views.hemeroteka'),
    (r'^(?P<article_slug>[\-\d\w]+)/$','csnews_multilingual.views.article_index'),
)

