from django.contrib import admin

from .models import (
    LoginLog,
    PedidoLog,
    ErroLog,
    CarrinhoAbandonadoLog,
    CheckoutVisitado
)

@admin.register(LoginLog)
class LoginLogAdmin(admin.ModelAdmin):

    list_display = (
        'email',
        'evento',
        'sucesso',
        'ip',
        'criado_em'
    )

    list_filter = (
        'evento',
        'sucesso',
        'criado_em'
    )

    search_fields = (
        'email',
        'ip'
    )

    ordering = (
        '-criado_em',
    )


@admin.register(PedidoLog)
class PedidoLogAdmin(admin.ModelAdmin):

    list_display = (
        'pedido_id',
        'evento',
        'usuario',
        'criado_em'
    )

    list_filter = (
        'evento',
        'criado_em'
    )

    search_fields = (
        'pedido_id',
    )

    ordering = (
        '-criado_em',
    )


@admin.register(ErroLog)
class ErroLogAdmin(admin.ModelAdmin):

    list_display = (
        'url',
        'erro',
        'criado_em'
    )

    search_fields = (
        'url',
        'erro'
    )

    ordering = (
        '-criado_em',
    )


@admin.register(CarrinhoAbandonadoLog)
class CarrinhoAbandonadoLogAdmin(admin.ModelAdmin):

    list_display = (
        'usuario_email',
        'valor_total',
        'quantidade_itens',
        'criado_em'
    )

    ordering = (
        '-criado_em',
    )
    
@admin.register(CheckoutVisitado)
class CheckoutVisitadoAdmin(admin.ModelAdmin):

    list_display = (
        'usuario',
        'valor_total',
        'quantidade_itens',
        'checkout_em',
        'processado'
    )

    list_filter = (
        'processado',
    )

    ordering = (
        '-checkout_em',
    )