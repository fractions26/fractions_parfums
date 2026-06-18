from django.urls import path

from . import views


urlpatterns = [

    path(
        '',
        views.pagamento,
        name='pagamento'
    ),

    path(
        'parcelas/',
        views.consultar_parcelas_checkout,
        name='consultar_parcelas_checkout'
    ),

]
