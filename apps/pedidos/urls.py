from django.urls import path

from . import views


urlpatterns = [

    path(
        'checkout/',
        views.checkout,
        name='checkout'
    ),

    path(
        'calcular-frete/',
        views.calcular_frete_checkout,
        name='calcular_frete_checkout'
    ),

    path(
        'pedido/<str:codigo>/',
        views.detalhe_pedido,
        name='detalhe_pedido'
    ),

]