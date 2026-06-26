from django.urls import path

from .views import validar_cupom

urlpatterns = [

    path(
        'validar/',
        validar_cupom,
        name='validar_cupom'
    ),

]