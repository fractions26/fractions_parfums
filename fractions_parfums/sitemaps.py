from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticSitemap(Sitemap):

    changefreq = "daily"
    priority = 1.0

    def items(self):
        return [
            "home",
            "categoria_masculinos",
            "categoria_femininos",
            "categoria_arabes",
            "quem_somos",
        ]

    def location(self, item):

        if item == "home":
            return reverse("home")

        if item == "categoria_masculinos":
            return "/produtos/categoria/masculinos/"

        if item == "categoria_femininos":
            return "/produtos/categoria/femininos/"

        if item == "categoria_arabes":
            return "/produtos/categoria/arabes/"

        if item == "quem_somos":
            return "/quem-somos/"

    def priority(self, item):

        prioridades = {
            "home": 1.0,
            "categoria_masculinos": 0.9,
            "categoria_femininos": 0.9,
            "categoria_arabes": 0.9,
            "quem_somos": 0.6,
        }

        return prioridades.get(item, 0.5)