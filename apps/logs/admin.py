from django.contrib import admin

from .models import (
    LoginLog,
    PedidoLog,
    ErroLog,
    CarrinhoAbandonadoLog,
    CheckoutVisitado,
    AcessoPagina
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

    date_hierarchy = 'criado_em'

    ordering = (
        '-criado_em',
    )


@admin.register(PedidoLog)
class PedidoLogAdmin(admin.ModelAdmin):

    list_display = (
        'pedido_id',
        'codigo_pedido',
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
        'codigo_pedido',
        'usuario__email'
    )

    date_hierarchy = 'criado_em'

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

    date_hierarchy = 'criado_em'

    ordering = (
        '-criado_em',
    )


@admin.register(CarrinhoAbandonadoLog)
class CarrinhoAbandonadoLogAdmin(admin.ModelAdmin):

    list_display = (
        'usuario_email',
        'valor_total',
        'quantidade_itens',
        'itens_removidos',
        'checkout_em',
        'criado_em'
    )

    list_filter = (
        'itens_removidos',
        'checkout_em'
    )

    search_fields = (
        'usuario_email',
    )

    date_hierarchy = 'criado_em'

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
        'email_1_enviado',
        'email_2_enviado',
        'email_3_enviado',
        'processado',
    )

    list_filter = (
        'processado',
        'email_1_enviado',
        'email_2_enviado',
        'email_3_enviado',
    )

    search_fields = (
        'usuario__email',
    )

    date_hierarchy = 'checkout_em'

    ordering = (
        '-checkout_em',
    )

    
from django.urls import path
from django.template.response import TemplateResponse
from django.utils import timezone

from datetime import timedelta
from collections import defaultdict


from django.contrib.admin.views.decorators import staff_member_required


@staff_member_required
def dashboard_acessos(request):

    periodo = request.GET.get(
        'periodo',
        'hoje'
    )

    fim = timezone.now()

    if periodo == 'ontem':

        inicio = (
            timezone.now().replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0
            )
            - timedelta(days=1)
        )

        fim = inicio + timedelta(days=1)

    elif periodo == '7':

        inicio = fim - timedelta(days=7)

    elif periodo == '30':

        inicio = fim - timedelta(days=30)

    else:

        inicio = timezone.now().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

    acessos = AcessoPagina.objects.filter(
        criado_em__gte=inicio,
        criado_em__lte=fim
    )

    home = acessos.filter(
        tipo='HOME'
    )

    produtos = acessos.filter(
        tipo='PRODUTO'
    )

    pedidos = acessos.filter(
        tipo='PEDIDO'
    )

    home_por_hora = defaultdict(int)
    produtos_por_hora = defaultdict(int)
    pedidos_por_hora = defaultdict(int)

    for acesso in home:
        home_por_hora[
            acesso.criado_em.hour
        ] += 1

    for acesso in produtos:
        produtos_por_hora[
            acesso.criado_em.hour
        ] += 1

    for acesso in pedidos:
        pedidos_por_hora[
            acesso.criado_em.hour
        ] += 1

    context = admin.site.each_context(
        request
    )

    context.update({

        'title': 'Dashboard de Acessos',

        'periodo': periodo,

        'total_home': home.count(),

        'total_produtos': produtos.count(),

        'total_pedidos': pedidos.count(),

        'home_por_hora': dict(
            sorted(home_por_hora.items())
        ),

        'produtos_por_hora': dict(
            sorted(produtos_por_hora.items())
        ),

        'pedidos_por_hora': dict(
            sorted(pedidos_por_hora.items())
        ),

    })

    return TemplateResponse(
        request,
        'admin/logs/dashboard.html',
        context
    )


original_get_urls = admin.site.get_urls


def custom_get_urls():

    urls = [

        path(
            'dashboard/',
            admin.site.admin_view(
                dashboard_acessos
            ),
            name='dashboard-acessos'
        )

    ]

    return urls + original_get_urls()


admin.site.get_urls = custom_get_urls