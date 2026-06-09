from django.urls import path

from . import views


urlpatterns = [

    path(
        'enderecos/',
        views.meus_enderecos,
        name='meus_enderecos'
    ),

]