from django.contrib import admin
from django.contrib import messages

from .models import Pedido
from .models import ItemPedido

from apps.pagamentos.services import (
    reembolsar_pagamento,
    consultar_pagamento,
)

from apps.pedidos.melhor_envio import (
    inserir_frete_carrinho,
    comprar_etiqueta,
    consultar_envio,
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
        'enviar_para_melhor_envio',
        'consultar_status_melhor_envio',
        'comprar_etiqueta_melhor_envio',
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

    def enviar_para_melhor_envio(
        self,
        request,
        queryset
    ):

        for pedido in queryset:

            if pedido.melhor_envio_id:

                self.message_user(
                    request,
                    f'Pedido {pedido.codigo} já possui envio criado.',
                    messages.WARNING
                )

                continue

            print("=" * 80)

            print(
                f"ENVIANDO PEDIDO {pedido.codigo}"
            )

            resultado = inserir_frete_carrinho(
                pedido
            )

            body = resultado.get(
                "body",
                {}
            )

            if resultado.get("status_code") == 201:

                pedido.melhor_envio_id = body.get(
                    "id"
                )

                pedido.status_envio = body.get(
                    "status",
                    ""
                )

                pedido.transportadora = (
                    pedido.frete_nome
                )

                pedido.save()

                print(
                    "✅ DADOS SALVOS NO PEDIDO"
                )

                self.message_user(
                    request,
                    f'Pedido {pedido.codigo} enviado para o Melhor Envio com sucesso.',
                    messages.SUCCESS
                )

            else:

                self.message_user(
                    request,
                    f'Erro {resultado.get("status_code")} ao criar envio.',
                    messages.ERROR
                )

            print("STATUS_CODE")
            print(
                resultado.get(
                    "status_code"
                )
            )

            print("BODY")
            print(body)

            print("=" * 80)

    enviar_para_melhor_envio.short_description = (
        '📦 Enviar Para Melhor Envio'
    )

    def consultar_status_melhor_envio(
        self,
        request,
        queryset
    ):

        for pedido in queryset:

            if not pedido.melhor_envio_id:

                self.message_user(
                    request,
                    f'Pedido {pedido.codigo} sem Melhor Envio ID.',
                    messages.ERROR
                )

                continue

            resultado = consultar_envio(
                pedido
            )

            status_code = resultado.get(
                "status_code"
            )

            body = resultado.get(
                "body",
                {}
            )

            print("=" * 80)
            print("CONSULTA ENVIO")

            print("PEDIDO")
            print(pedido.codigo)

            print("STATUS_CODE")
            print(status_code)

            print("BODY")
            print(body)

            print("=" * 80)

            if status_code == 200:

                envio = body.get(
                    pedido.melhor_envio_id,
                    {}
                )

                pedido.status_envio = envio.get(
                    "status",
                    pedido.status_envio
                )

                pedido.melhor_envio_protocolo = envio.get(
                    "protocol",
                    pedido.melhor_envio_protocolo
                )

                pedido.codigo_rastreio = (
                    envio.get("tracking")
                    or pedido.codigo_rastreio
                )

                pedido.save()

                self.message_user(
                    request,
                    (
                        f'Pedido {pedido.codigo} atualizado. '
                        f'Status: {pedido.status_envio}'
                    ),
                    messages.SUCCESS
                )

            else:

                self.message_user(
                    request,
                    f'Erro {status_code} ao consultar envio.',
                    messages.ERROR
                )

    consultar_status_melhor_envio.short_description = (
        '📋 Consultar Status Melhor Envio'
    )
    
    def comprar_etiqueta_melhor_envio(
        self,
        request,
        queryset
    ):

        for pedido in queryset:

            if not pedido.melhor_envio_id:

                self.message_user(
                    request,
                    f'Pedido {pedido.codigo} sem Melhor Envio ID.',
                    messages.ERROR
                )

                continue

            resultado = comprar_etiqueta(
                pedido
            )

            status_code = resultado.get(
                "status_code"
            )

            body = resultado.get(
                "body",
                {}
            )

            print("=" * 80)
            print("COMPRA ETIQUETA")
            print("PEDIDO")
            print(pedido.codigo)
            print("STATUS_CODE")
            print(status_code)
            print("BODY")
            print(body)
            print("=" * 80)

            if status_code in [200, 201]:

                pedido.etiqueta_gerada = True

                pedido.save()

                self.message_user(
                    request,
                    f'Etiqueta do pedido {pedido.codigo} comprada com sucesso.',
                    messages.SUCCESS
                )

            else:

                self.message_user(
                    request,
                    f'Erro ao comprar etiqueta do pedido {pedido.codigo}.',
                    messages.ERROR
                )


    comprar_etiqueta_melhor_envio.short_description = (
        '🏷️ Comprar Etiqueta Melhor Envio'
    )