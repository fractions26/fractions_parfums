from django.urls import path
from .views import home, contato, criar_conta, login_usuario, logout_usuario, quem_somos, politica_privacidade, trocas_devolucao, perguntas_frequentes, minha_conta

urlpatterns = [
    path('', home, name='home'),
    path('contato/', contato, name='contato'),
    path('criar-conta/', criar_conta, name='criar_conta'),

    path('login/', login_usuario, name='login'),
    path('logout/', logout_usuario, name='logout'),

    # ✅ MINHA CONTA
    path('minha-conta/', minha_conta, name='minha_conta'),

    # ✅ NOVOS
    path('quem-somos/', quem_somos, name='quem_somos'),
    path('politica-privacidade/', politica_privacidade, name='politica_privacidade'),
    path('trocas-devolucoes/', trocas_devolucao, name='trocas_devolucao'),
    path('perguntas-frequentes/', perguntas_frequentes, name='perguntas_frequentes'),

]