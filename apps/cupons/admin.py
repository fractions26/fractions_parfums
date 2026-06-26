# apps/cupons/admin.py

from django.contrib import admin

from .models import Cupom


@admin.register(Cupom)
class CupomAdmin(admin.ModelAdmin):

    list_display = (
        'codigo',
        'desconto_percentual',
        'ativo',
        'primeira_compra',
        'data_inicio',
        'data_fim',
    )

    search_fields = (
        'codigo',
        'descricao',
    )

    list_filter = (
        'ativo',
        'primeira_compra',
    )
    
    
    