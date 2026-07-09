from django.urls import path

from .views import (
    detalhe_produto,
    lista_categoria,
    lista_produtos,
    detalhes_pagamento,
    busca_ajax,
    avaliar_produto
)

from fractions_parfums.sitemaps import (
    StaticSitemap,
    PerfumeSitemap,
)

sitemaps = {
    "static": StaticSitemap,
    "produtos": PerfumeSitemap,
}

urlpatterns = [

    # ✅ LISTA GERAL
    path(
        '',
        lista_produtos,
        name='lista_produtos'
    ),

    # ✅ LISTA POR CATEGORIA
    path(
        'categoria/<slug:slug>/',
        lista_categoria,
        name='lista_categoria'
    ),

    # ✅ PAGAMENTO
    path(
        'pagamento/<int:perfume_id>/',
        detalhes_pagamento,
        name='detalhes_pagamento'
    ),

    # ✅ DETALHE PRODUTO
    path(
        'detalhe/<slug:slug>/',
        detalhe_produto,
        name='detalhe_produto'
    ),

    # ✅ AVALIAR PRODUTO
    path(
        'avaliar/<int:perfume_id>/',
        avaliar_produto,
        name='avaliar_produto'
    ),

    # ✅ BUSCA AJAX
    path(
        'busca/ajax/',
        busca_ajax,
        name='busca_ajax'
    ),
]