from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from apps.produtos.models import Produto


# ✅ PÁGINAS ESTÁTICAS
class StaticSitemap(Sitemap):

    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'home',
            'categoria_masculinos',
            'categoria_femininos',
            'categoria_arabes',
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

        if item == 'quem_somos':
            return '/quem-somos/'


# ✅ PRODUTOS (ESSENCIAL)
class ProdutoSitemap(Sitemap):

    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Produto.objects.all()  # ✅ pega todos

    def location(self, obj):
        return f"/produtos/detalhe/{obj.slug}/"