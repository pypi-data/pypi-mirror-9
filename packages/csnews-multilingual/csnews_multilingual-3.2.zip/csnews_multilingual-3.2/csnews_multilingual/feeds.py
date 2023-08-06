from django.contrib.syndication.views import Feed
from csnews_multilingual.models import Article

class LatestNews(Feed):
    title = 'Ahotsak: Albisteak'
    link = '/albisteak/'
    description = 'Ahotsak.com Euskal Herriko hizkerak eta ahozko ondarea'

    title_template = 'feeds/rss_title.html'
    description_template = 'feeds/rss_description.html'

    def items(self):
        return Article.objects.filter(is_public=True).order_by('-published')[:20]

    def item_pubdate(self,item):
        return item.published

    def item_link(self,item):
        return u'{% url "csnews_article" item.slug %}?utm_source=rss_link&utm_medium=rss&utm_campaign=rss_feed'
