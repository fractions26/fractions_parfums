from django.urls import path

from .views import (
    calcular_frete,
    gerar_token_melhor_envio,
)

urlpatterns = [

    path(
        'frete/',
        calcular_frete,
        name='calcular_frete'
    ),

    path(
        'gerar-token/',
        gerar_token_melhor_envio,
        name='gerar_token_melhor_envio'
    ),

]