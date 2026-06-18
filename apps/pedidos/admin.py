from django.contrib import admin
from django.contrib import messages

from .models import Pedido
from .models import ItemPedido

from apps.pagamentos.services import (
    reembolsar_pagamento
)


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0


def reembolsar_pagamentos(
    modeladmin,
    request,
    queryset
):

    sucesso = 0

    for pedido in queryset:

        if not pedido.mercadopago_payment_id:
            continue

        if pedido.status != 'PAGO':
            continue

        resultado = reembolsar_pagamento(
            pedido.mercadopago_payment_id
        )

        if resultado.get('id'):

            pedido.status = 'REEMBOLSADO'
            pedido.save()

            sucesso += 1

    modeladmin.message_user(
        request,
        f'{sucesso} pedido(s) reembolsado(s) com sucesso.',
        messages.SUCCESS
    )


reembolsar_pagamentos.short_description = (
    '💰 Reembolsar pagamentos selecionados'
)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):

    list_display = (
        'codigo',
        'usuario',
        'total',
        'status',
        'criado_em',
    )

    actions = ['reembolsar_pagamentos']

    def reembolsar_pagamentos(
        self,
        request,
        queryset
    ):

        sucesso = 0

        for pedido in queryset:

            if not pedido.mercadopago_payment_id:
                continue

            if pedido.status != 'PAGO':
                continue

            resultado = reembolsar_pagamento(
                pedido.mercadopago_payment_id
            )

            print(
                'REEMBOLSO:',
                resultado
            )

            if resultado.get('id'):

                pedido.status = 'REEMBOLSADO'

                pedido.save()

                sucesso += 1

        self.message_user(
            request,
            f'{sucesso} pedido(s) reembolsado(s) com sucesso.',
            messages.SUCCESS
        )

    reembolsar_pagamentos.short_description = (
        '💰 Reembolsar pagamentos selecionados'
    )