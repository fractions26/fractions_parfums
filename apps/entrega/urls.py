from django.urls import path
from .views import calcular_frete

urlpatterns = [
    path('frete/', calcular_frete, name='calcular_frete'),
]