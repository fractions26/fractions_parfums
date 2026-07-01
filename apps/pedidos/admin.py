from django.contrib import admin
from django.contrib import messages

from .models import Pedido
from .models import ItemPedido

from apps.pagamentos.services import (
    reembolsar_pagamento,
    consultar_pagamento,
)


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
        'transportadora',
        'codigo_rastreio',
        'etiqueta_gerada',
        'status_envio',
        'criado_em',
    )

    list_filter = (
        'status',
        'etiqueta_gerada',
        'status_envio',
        'transportadora',
        'criado_em',
    )

    search_fields = (
        'codigo',
        'email',
        'codigo_rastreio',
        'transportadora',
    )

    readonly_fields = (
        'melhor_envio_id',
        'codigo_rastreio',
        'transportadora',
        'url_etiqueta',
        'status_envio',
    )

    fieldsets = (

        (
            'Pedido',
            {
                'fields': (
                    'codigo',
                    'usuario',
                    'status',
                    'subtotal',
                    'frete',
                    'total',
                )
            }
        ),

        (
            'Cliente',
            {
                'fields': (
                    'nome',
                    'email',
                    'telefone',
                    'cpf',
                )
            }
        ),

        (
            'Endereço',
            {
                'fields': (
                    'cep',
                    'endereco',
                    'numero',
                    'complemento',
                    'cidade',
                    'estado',
                )
            }
        ),

        (
            'Mercado Pago',
            {
                'fields': (
                    'mercadopago_payment_id',
                    'mercadopago_status',
                    'metodo_pagamento',
                    'parcelas',
                )
            }
        ),

        (
            'Melhor Envio',
            {
                'fields': (
                    'melhor_envio_id',
                    'transportadora',
                    'codigo_rastreio',
                    'status_envio',
                    'url_etiqueta',
                    'etiqueta_gerada',
                )
            }
        ),

    )

    inlines = [ItemPedidoInline]

    actions = [
        'consultar_mercadopago',
        'sincronizar_mercadopago',
        'reembolsar_pagamentos',
    ]

    def consultar_mercadopago(
        self,
        request,
        queryset
    ):

        for pedido in queryset:

            if not pedido.mercadopago_payment_id:

                print(
                    f'PEDIDO {pedido.codigo} SEM PAYMENT_ID'
                )

                continue

            resultado = consultar_pagamento(
                pedido.mercadopago_payment_id
            )

            print(
                f'CONSULTA MP PEDIDO={pedido.codigo}'
            )

            print(resultado)

        self.message_user(
            request,
            'Consulta Mercado Pago executada. Verifique os logs.',
            messages.SUCCESS
        )

    consultar_mercadopago.short_description = (
        '🔍 Consultar Mercado Pago'
    )

    def sincronizar_mercadopago(
        self,
        request,
        queryset
    ):

        atualizados = 0

        for pedido in queryset:

            if not pedido.mercadopago_payment_id:
                continue

            dados = consultar_pagamento(
                pedido.mercadopago_payment_id
            )

            print(
                f'SINCRONIZANDO PEDIDO={pedido.codigo}'
            )

            print(dados)

            pedido.mercadopago_status = (
                dados.get('status', '')
            )

            valor_reembolsado = (
                dados.get(
                    'transaction_amount_refunded',
                    0
                )
            )

            if valor_reembolsado > 0:

                pedido.status = 'REEMBOLSADO'

            elif dados.get('status') == 'approved':

                pedido.status = 'PAGO'

            elif dados.get('status') == 'cancelled':

                pedido.status = 'CANCELADO'

            pedido.save()

            atualizados += 1

        self.message_user(
            request,
            f'{atualizados} pedido(s) sincronizado(s).',
            messages.SUCCESS
        )

    sincronizar_mercadopago.short_description = (
        '🔄 Sincronizar Status Mercado Pago'
    )

    def reembolsar_pagamentos(
        self,
        request,
        queryset
    ):

        sucesso = 0

        for pedido in queryset:

            print(
                f'PROCESSANDO PEDIDO={pedido.codigo}'
            )

            if not pedido.mercadopago_payment_id:

                print(
                    f'PEDIDO {pedido.codigo} SEM PAYMENT_ID'
                )

                continue

            dados = consultar_pagamento(
                pedido.mercadopago_payment_id
            )

            mp_status = dados.get('status')

            valor_reembolsado = (
                dados.get(
                    'transaction_amount_refunded',
                    0
                )
            )

            print(
                f'MP_STATUS={mp_status}'
            )

            print(
                f'VALOR_REEMBOLSADO={valor_reembolsado}'
            )

            if valor_reembolsado > 0:

                print(
                    f'PEDIDO {pedido.codigo} JA REEMBOLSADO'
                )

                continue

            if mp_status != 'approved':

                print(
                    f'PEDIDO {pedido.codigo} NAO ESTA APPROVED'
                )

                continue

            resultado = reembolsar_pagamento(
                pedido.mercadopago_payment_id
            )

            print(
                'REEMBOLSO:',
                resultado
            )

            if (
                resultado.get('id')
                or resultado.get('payment_id')
            ):

                pedido.status = 'REEMBOLSADO'

                pedido.mercadopago_status = (
                    resultado.get(
                        'status',
                        'refunded'
                    )
                )

                pedido.save()

                sucesso += 1

            else:

                print(
                    'FALHA REEMBOLSO:',
                    resultado
                )

        self.message_user(
            request,
            f'{sucesso} pedido(s) reembolsado(s) com sucesso.',
            messages.SUCCESS
        )

    reembolsar_pagamentos.short_description = (
        '💰 Reembolsar Pagamentos'
    )