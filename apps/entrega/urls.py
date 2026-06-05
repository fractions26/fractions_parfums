from django.urls import path
from .views import checkout, calcular_frete

urlpatterns = [
    # ✅ página de checkout
    path('', checkout, name='checkout'),

    # 🔥 rota do frete (ESSA FALTAVA)
    path('frete/', calcular_frete, name='calcular_frete'),
]