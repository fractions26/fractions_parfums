from django.contrib import admin

from .models import Pedido
from .models import ItemPedido


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):

    list_display = (
        'codigo',
        'usuario',
        'total',
        'status',
        'criado_em',
    )

    list_filter = (
        'status',
        'criado_em',
    )

    search_fields = (
        'codigo',
        'email',
    )

    inlines = [ItemPedidoInline]