from django.urls import path
from .views import (
    ver_carrinho,
    adicionar_carrinho,
    atualizar_item,
    quantidade_carrinho,
    remover_item
)

urlpatterns = [

    # ✅ Página completa do carrinho
    path('', ver_carrinho, name='carrinho'),

    # ✅ Drawer (AJAX)
    path('drawer/', ver_carrinho, name='carrinho_drawer'),

    # ✅ Ações
    path('adicionar/', adicionar_carrinho, name='adicionar_carrinho'),
    path('atualizar/', atualizar_item, name='atualizar_item'),
    path('remover/', remover_item, name='remover_item'),
    path('quantidade/', quantidade_carrinho, name='quantidade_carrinho'),
]
