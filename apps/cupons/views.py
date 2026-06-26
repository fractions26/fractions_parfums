from decimal import Decimal

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Cupom
from apps.pedidos.models import Pedido


@login_required
def validar_cupom(request):

    codigo = (
        request.GET.get("codigo", "")
        .strip()
        .upper()
    )

    subtotal = Decimal(
        request.GET.get("subtotal", "0")
    )

    if not codigo:

        return JsonResponse({
            "success": False,
            "erro": "Informe um cupom."
        })

    cupom = Cupom.objects.filter(
        codigo=codigo,
        ativo=True
    ).first()

    if not cupom:

        return JsonResponse({
            "success": False,
            "erro": "Cupom inválido."
        })

    agora = timezone.now()

    if cupom.data_inicio and agora < cupom.data_inicio:

        return JsonResponse({
            "success": False,
            "erro": "Cupom ainda não está disponível."
        })

    if cupom.data_fim and agora > cupom.data_fim:

        return JsonResponse({
            "success": False,
            "erro": "Cupom expirado."
        })

    if cupom.primeira_compra:

        possui_pedido = Pedido.objects.filter(
            usuario=request.user
        ).exclude(
            status='CANCELADO'
        ).exists()

        if possui_pedido:

            return JsonResponse({
                "success": False,
                "erro": "Cupom válido apenas para primeira compra."
            })

    desconto = (
        subtotal *
        cupom.desconto_percentual
    ) / Decimal("100")

    return JsonResponse({
        "success": True,
        "codigo": cupom.codigo,
        "percentual": float(
            cupom.desconto_percentual
        ),
        "desconto": float(desconto)
    })