from django.contrib.sitemaps import Sitemap

class StaticSitemap(Sitemap):
    def items(self):
        return ['home']

    def location(self, item):
        return '/'
