from django.urls import path
from .views import (
    detalhe_produto,
    lista_categoria,
    lista_produtos,
    detalhes_pagamento
)

urlpatterns = [

    # ✅ ESSA LINHA RESOLVE O ERRO
    path('', lista_produtos, name='lista_produtos_root'),

    path('categoria/<slug:slug>/', lista_categoria, name='lista_categoria'),
    path('todos/', lista_produtos, name='lista_produtos'),

    # ✅ PAGAMENTO
    path('pagamento/<int:perfume_id>/', detalhes_pagamento, name='detalhes_pagamento'),

    # ✅ SEMPRE POR ÚLTIMO
    path('<slug:slug>/', detalhe_produto, name='detalhe_produto'),
]