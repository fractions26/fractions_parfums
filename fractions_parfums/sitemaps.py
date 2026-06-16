from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticSitemap(Sitemap):

    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return [
            'home',
            'categoria_masculinos',
            'categoria_femininos',
            'categoria_arabes',
            'produtos',
            'quem_somos',
        ]

    def location(self, item):

        if item == 'home':
            return reverse('home')

        if item == 'categoria_masculinos':
            return '/produtos/categoria/masculinos/'

        if item == 'categoria_femininos':
            return '/produtos/categoria/femininos/'

        if item == 'categoria_arabes':
            return '/produtos/categoria/arabes/'

        if item == 'produtos':
            return '/produtos/'

        if item == 'quem_somos':
            return '/quem-somos/'