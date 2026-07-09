from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.produtos.models import Perfume


class StaticSitemap(Sitemap):

    def items(self):
        return [
            "home",
            "categoria_masculinos",
            "categoria_femininos",
            "categoria_arabes",
            "quem_somos",
            "o_que_e_decant",
            "contato",
            "perguntas_frequentes",
            "trocas_devolucao",
            "politica_privacidade",
        ]

    def location(self, item):

        urls = {
            "home": reverse("home"),

            # Categorias
            "categoria_masculinos": "/produtos/categoria/masculinos/",
            "categoria_femininos": "/produtos/categoria/femininos/",
            "categoria_arabes": "/produtos/categoria/arabes/",

            # Institucionais
            "quem_somos": reverse("quem_somos"),
            "o_que_e_decant": reverse("o_que_e_decant"),
            "contato": reverse("contato"),
            "perguntas_frequentes": reverse("perguntas_frequentes"),
            "trocas_devolucao": reverse("trocas_devolucao"),
            "politica_privacidade": reverse("politica_privacidade"),
        }

        return urls[item]

    def priority(self, item):

        prioridades = {
            "home": 1.0,

            "categoria_masculinos": 0.9,
            "categoria_femininos": 0.9,
            "categoria_arabes": 0.9,

            "quem_somos": 0.7,
            "o_que_e_decant": 0.7,

            "contato": 0.6,
            "perguntas_frequentes": 0.6,

            "trocas_devolucao": 0.5,
            "politica_privacidade": 0.5,
        }

        return prioridades.get(item, 0.5)

    def changefreq(self, item):

        frequencias = {
            "home": "daily",

            "categoria_masculinos": "daily",
            "categoria_femininos": "daily",
            "categoria_arabes": "daily",

            "quem_somos": "monthly",
            "o_que_e_decant": "monthly",
            "contato": "monthly",
            "perguntas_frequentes": "monthly",
            "trocas_devolucao": "monthly",
            "politica_privacidade": "monthly",
        }

        return frequencias.get(item, "monthly")


class PerfumeSitemap(Sitemap):

    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return (
            Perfume.objects
            .filter(ativo=True)
            .order_by("nome")
        )

    def location(self, obj):
        return reverse(
            "detalhe_produto",
            kwargs={
                "slug": obj.slug
            }
        )