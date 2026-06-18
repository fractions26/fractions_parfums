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
from apps.pagamentos.services import get_mp_public_key

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from decimal import Decimal
import re

@login_required(login_url='login')
def checkout(request):

    # ✅ CARRINHO
    carrinho = get_carrinho(request)

    if not carrinho or not hasattr(carrinho, 'itens'):
        messages.warning(request, "Seu carrinho está vazio.")
        return redirect('carrinho')

    itens = carrinho.itens.select_related('perfume')

    if not itens.exists():
        messages.warning(request, "Seu carrinho está vazio.")
        return redirect('home')

    # ✅ ENDEREÇO
    endereco_principal = Endereco.objects.filter(
        usuario=request.user,
        principal=True
    ).first()

    # ✅ TOTAL
    total = sum(
        (item.preco or 0) * (item.quantidade or 0)
        for item in itens
    )

    # =====================================
    # ✅ POST (FINALIZAR PEDIDO)
    # =====================================
    if request.method == 'POST':
        
        print(
            f"CARD TOKEN: {request.POST.get('card_token')}"
        )

        print(
            f"METODO: {request.POST.get('metodo_pagamento')}"
        )
        

        # =========================
        # ✅ CPF (OBRIGATÓRIO)
        # =========================
        perfil = getattr(request.user, 'perfil', None)

        cpf_input = request.POST.get('cpf_pagamento') or ''
        cpf_perfil = perfil.cpf if perfil and perfil.cpf else ''

        cpf = cpf_input or cpf_perfil

        # ✅ VALIDA OBRIGATÓRIO
        if not cpf:
            messages.error(request, "❌ Informe o CPF para continuar.")
            return redirect('checkout')

        # ✅ GARANTE STRING + LIMPA
        cpf = str(cpf)
        cpf = re.sub(r'\D', '', cpf)

        # ✅ VALIDA TAMANHO
        if len(cpf) != 11:
            messages.error(request, "❌ CPF inválido.")
            return redirect('checkout')

        # ✅ SALVA NO PERFIL (SE NÃO TIVER)
        if perfil and not getattr(perfil, 'cpf', None):
            perfil.cpf = cpf
            perfil.save()

        # =========================
        # ✅ FRETE
        # =========================
        frete_valor = request.POST.get('frete_valor') or '0'

        try:
            frete = Decimal(frete_valor)
        except:
            frete = Decimal('0')

        if frete <= 0:
            messages.warning(request, "Selecione um frete.")
            return redirect('checkout')

        # =========================
        # ✅ CRIA PEDIDO
        # =========================
        pedido = Pedido.objects.create(
            usuario=request.user,
            codigo=gerar_codigo_pedido(),

            subtotal=total,
            frete=frete,
            total=total + frete,

            metodo_pagamento=request.POST.get(
                'metodo_pagamento',
                ''
            ),

            cpf=cpf,

            frete_nome=request.POST.get('frete_nome', ''),
            frete_prazo=request.POST.get('frete_prazo', ''),

            nome=request.user.get_full_name(),
            email=request.user.email,
            telefone=(endereco_principal.telefone if endereco_principal else ''),

            cep=(endereco_principal.cep if endereco_principal else ''),
            endereco=(endereco_principal.endereco if endereco_principal else ''),
            numero=(endereco_principal.numero if endereco_principal else ''),
            complemento=(endereco_principal.complemento if endereco_principal else ''),
            cidade=(endereco_principal.cidade if endereco_principal else ''),
            estado=(endereco_principal.estado if endereco_principal else ''),
        )

        # =========================
        # ✅ ITENS
        # =========================
        for item in itens:
            ItemPedido.objects.create(
                pedido=pedido,
                perfume=item.perfume,
                produto_nome=item.perfume.nome,
                tamanho=item.tamanho,
                quantidade=item.quantidade,
                preco=item.preco,
                subtotal=(item.preco * item.quantidade)
            )

        # =========================
        # ✅ LIMPA CARRINHO
        # =========================
        itens.delete()

        # =========================
        # ✅ SUCESSO
        # =========================
        messages.success(
            request,
            f"✅ Pedido #{pedido.codigo} realizado com sucesso!"
        )

        return redirect('detalhe_pedido', codigo=pedido.codigo)


    # =========================
    # ✅ GET (carrega página)
    # =========================
    return render(
        request,
        'pedidos/checkout.html',
        {
            'itens': itens,
            'total': total,
            'endereco_principal': endereco_principal,

            # Mercado Pago
            'mp_public_key': get_mp_public_key(),
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