from django.contrib.sitemaps import Sitemap
from authors.models import Author
from content.models import Article, Case, Event, Issue, Topic


class AuthorSitemap(Sitemap):
    changefreq = "always"
    priority = 0.5

    def items(self):
        return Author.objects.all()


class ArticleSitemap(Sitemap):
    changefreq="weekly"
    priority = 0.9

    def items(self):
        return Article.objects.all()

    def last_mod(self, obj):
        return obj.date_label


class TopicSitemap(Sitemap):
    changefreq="monthly"
    priority = 0.5

    def items(self):
        return Topic.objects.all()


class IssueSitemap(Sitemap):
    chagefreq="monthly"
    priority=0.5

    def items(self):
        return Issue.objects.all()


class EventSitemap(Sitemap):
    changefreq="always"
    priority=0.9

    def items(self):
        return Event.objects.all()


class CaseSitemap(Sitemap):
    changefreq="monthly"
    priority=0.5

    def items(self):
        return Case.objects.all()

    def last_mod(self, obj):
        return obj.date_label
