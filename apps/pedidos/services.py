import uuid


def gerar_codigo_pedido():

    return str(uuid.uuid4())[:8].upper()


def baixar_estoque_pedido(pedido):

    # ✅ EVITA DUPLA BAIXA
    if pedido.estoque_baixado:
        return

    for item_pedido in pedido.itens.select_related(
        'perfume'
    ):

        if not item_pedido.perfume:
            continue

        try:

            tamanho_ml = int(
                ''.join(
                    filter(
                        str.isdigit,
                        item_pedido.tamanho
                    )
                )
            )

        except Exception:

            continue

        ml_vendido = (
            tamanho_ml *
            item_pedido.quantidade
        )

        perfume = item_pedido.perfume

        perfume.estoque_ml = max(
            0,
            perfume.estoque_ml - ml_vendido
        )

        perfume.save()

    pedido.estoque_baixado = True

    pedido.save(
        update_fields=[
            'estoque_baixado'
        ]
    )