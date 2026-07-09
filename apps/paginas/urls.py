from django.urls import path
from .views import (
    home,
    contato,
    criar_conta,
    login_usuario,
    logout_usuario,
    quem_somos,
    o_que_e_decant,          # ✅ NOVO
    politica_privacidade,
    trocas_devolucao,
    perguntas_frequentes,
    minha_conta,
    editar_dados,
    editar_endereco,
)

urlpatterns = [
    path('', home, name='home'),

    path('contato/', contato, name='contato'),
    path('criar-conta/', criar_conta, name='criar_conta'),

    path('login/', login_usuario, name='login'),
    path('logout/', logout_usuario, name='logout'),

    # Minha Conta
    path('minha-conta/', minha_conta, name='minha_conta'),

    # Páginas Institucionais
    path('quem-somos/', quem_somos, name='quem_somos'),

    path(
        'o-que-e-decant/',
        o_que_e_decant,
        name='o_que_e_decant'
    ),

    path(
        'politica-privacidade/',
        politica_privacidade,
        name='politica_privacidade'
    ),

    path(
        'trocas-devolucoes/',
        trocas_devolucao,
        name='trocas_devolucao'
    ),

    path(
        'perguntas-frequentes/',
        perguntas_frequentes,
        name='perguntas_frequentes'
    ),

    path(
        'editar-dados/',
        editar_dados,
        name='editar_dados'
    ),

    path(
        'editar-endereco/',
        editar_endereco,
        name='editar_endereco'
    ),
]