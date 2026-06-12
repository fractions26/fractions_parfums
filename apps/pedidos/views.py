from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings

import requests

from apps.carrinho.utils import get_carrinho
from apps.usuarios.models import Endereco

from .models import Pedido
from .models import ItemPedido

from .services import gerar_codigo_pedido


# =====================================
# ✅ CHECKOUT
# =====================================

@login_required
def checkout(request):

    carrinho = get_carrinho(request)

    itens = carrinho.itens.all()

    # ✅ ENDEREÇO PRINCIPAL
    endereco_principal = Endereco.objects.filter(
        usuario=request.user,
        principal=True
    ).first()

    total = sum(
        item.preco * item.quantidade
        for item in itens
    )

    # ✅ CRIA PEDIDO
    if request.method == 'POST':

        # ✅ FRETE DINÂMICO
        frete = Decimal(
            request.POST.get(
                'frete_valor',
                '0'
            )
        )

        pedido = Pedido.objects.create(

            usuario=request.user,

            codigo=gerar_codigo_pedido(),

            subtotal=total,

            frete=frete,

            frete_nome=request.POST.get(
                'frete_nome',
                ''
            ),

            frete_prazo=request.POST.get(
                'frete_prazo',
                ''
            ),

            total=total + frete,

            # ✅ DADOS USUÁRIO
            nome=request.user.get_full_name(),

            email=request.user.email,

            telefone=(
                endereco_principal.telefone
                if endereco_principal else ''
            ),

            # ✅ ENDEREÇO
            cep=(
                endereco_principal.cep
                if endereco_principal else ''
            ),

            endereco=(
                endereco_principal.endereco
                if endereco_principal else ''
            ),

            numero=(
                endereco_principal.numero
                if endereco_principal else ''
            ),

            complemento=(
                endereco_principal.complemento
                if endereco_principal else ''
            ),

            cidade=(
                endereco_principal.cidade
                if endereco_principal else ''
            ),

            estado=(
                endereco_principal.estado
                if endereco_principal else ''
            ),
        )

        # ✅ ITENS DO PEDIDO
        for item in itens:

            ItemPedido.objects.create(

                pedido=pedido,

                # ✅ RELAÇÃO COM O PRODUTO (ESSENCIAL)
                perfume=item.perfume,

                # ✅ DADOS SNAPSHOT
                produto_nome=item.perfume.nome,

                tamanho=item.tamanho,

                quantidade=item.quantidade,

                preco=item.preco,

                subtotal=(item.preco * item.quantidade)
            )


        # ✅ LIMPA CARRINHO
        itens.delete()

        # ✅ REDIRECIONA PAGAMENTO
        return redirect('pagamento')

    return render(
        request,
        'pedidos/checkout.html',
        {
            'itens': itens,
            'total': total,
            'endereco_principal': endereco_principal
        }
    )


# =====================================
# ✅ FRETE CHECKOUT AJAX
# =====================================

@login_required
def calcular_frete_checkout(request):

    endereco_principal = Endereco.objects.filter(
        usuario=request.user,
        principal=True
    ).first()

    if not endereco_principal:

        return JsonResponse({
            'success': False,
            'erro': 'Endereço não encontrado'
        })

    cep = endereco_principal.cep

    url = (
        "https://sandbox.melhorenvio.com.br"
        "/api/v2/me/shipment/calculate"
    )

    headers = {

        "Authorization": (
            f"Bearer "
            f"{settings.MELHOR_ENVIO_TOKEN}"
        ),

        "Accept": "application/json",

        "Content-Type": "application/json"
    }

    payload = {

        "from": {
            "postal_code": "82590100"
        },

        "to": {
            "postal_code": cep
        },

        "products": [
            {
                "id": "1",
                "width": 10,
                "height": 4,
                "length": 10,
                "weight": 0.2,
                "quantity": 1
            }
        ]
    }

    try:

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            verify=False
        )

        data = response.json()

        return JsonResponse({
            'success': True,
            'fretes': data
        })

    except Exception as e:

        return JsonResponse({
            'success': False,
            'erro': str(e)
        })
        
# =====================================
# ✅ DETALHE PEDIDO
# =====================================

@login_required
def detalhe_pedido(request, codigo):

    pedido = Pedido.objects.filter(
        usuario=request.user,
        codigo=codigo
    ).first()

    if not pedido:

        return redirect('minha_conta')

    return render(
        request,
        'pedidos/detalhe_pedido.html',
        {
            'pedido': pedido,
            'itens': pedido.itens.select_related('perfume')
        }
    )