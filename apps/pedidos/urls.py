from django.urls import path
from . import views

urlpatterns = [

    # ✅ CHECKOUT
    path(
        '',
        views.checkout,
        name='checkout'
    ),

    # ✅ FRETE AJAX
    path(
        'calcular-frete/',
        views.calcular_frete_checkout,
        name='calcular_frete_checkout'
    ),

    # ✅ DETALHE DO PEDIDO
    path(
        'pedido/<str:codigo>/',
        views.detalhe_pedido,
        name='detalhe_pedido'
    ),

]