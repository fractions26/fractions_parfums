from django.urls import path

from .views import (
    ver_carrinho,
    adicionar_carrinho,
    atualizar_item,
    quantidade_carrinho,
    remover_item,
    carrinhos_ativos
)

urlpatterns = [

    path(
        '',
        ver_carrinho,
        name='carrinho'
    ),

    path(
        'drawer/',
        ver_carrinho,
        name='carrinho_drawer'
    ),

    path(
        'adicionar/',
        adicionar_carrinho,
        name='adicionar_carrinho'
    ),

    path(
        'atualizar/',
        atualizar_item,
        name='atualizar_item'
    ),

    path(
        'remover/',
        remover_item,
        name='remover_item'
    ),

    path(
        'quantidade/',
        quantidade_carrinho,
        name='quantidade_carrinho'
    ),

    # ✅ NOVA VIEW
    path(
        'carrinhos-ativos/',
        carrinhos_ativos,
        name='carrinhos_ativos'
    ),
]