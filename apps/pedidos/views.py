from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings

import requests
import re

from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.carrinho.utils import get_carrinho
from apps.usuarios.models import Endereco

from .models import Pedido, ItemPedido
from .services import gerar_codigo_pedido

from apps.pagamentos.services import (
    get_mp_public_key,
    criar_pagamento_cartao,
    criar_pagamento_pix
)

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

        # =========================
        # ✅ CPF (OBRIGATÓRIO)
        # =========================
        perfil = getattr(request.user, 'perfil', None)

        cpf_input = request.POST.get('cpf_pagamento') or ''
        cpf_perfil = perfil.cpf if perfil and perfil.cpf else ''

        cpf = cpf_input or cpf_perfil

        if not cpf:
            messages.error(
                request,
                "❌ Informe o CPF para continuar."
            )
            return redirect('checkout')

        cpf = str(cpf)
        cpf = re.sub(r'\D', '', cpf)

        if len(cpf) != 11:
            messages.error(
                request,
                "❌ CPF inválido."
            )
            return redirect('checkout')

        if perfil and not getattr(perfil, 'cpf', None):
            perfil.cpf = cpf
            perfil.save()

        # =========================
        # ✅ FRETE
        # =========================
        frete_valor = request.POST.get(
            'frete_valor'
        ) or '0'

        try:
            frete = Decimal(frete_valor)

        except Exception:
            frete = Decimal('0')

        if frete <= 0:
            messages.warning(
                request,
                "Selecione um frete."
            )
            return redirect('checkout')

        # =========================
        # ✅ PAGAMENTO MP
        # =========================
        resultado_pagamento = None

        status_mp = ''

        payment_id = ''

        bandeira_cartao = ''

        status_pedido = 'PENDENTE'

        metodo_pagamento = request.POST.get(
            'metodo_pagamento'
        )

        print(
            "METODO RECEBIDO:",
            metodo_pagamento
        )

        # =========================
        # ✅ CARTÃO DE CRÉDITO
        # =========================
        if metodo_pagamento == 'novo_cartao':

            card_token = request.POST.get(
                'card_token'
            )

            if not card_token:

                messages.error(
                    request,
                    'Token do cartão não recebido.'
                )

                return redirect('checkout')

            resultado_pagamento = criar_pagamento_cartao(
                token=card_token,
                valor=total + frete,
                email=request.user.email,
                nome=request.user.get_full_name(),
                cpf=cpf
            )

            if resultado_pagamento is None:

                messages.error(
                    request,
                    'Erro ao processar pagamento.'
                )

                return redirect('checkout')

            status_mp = resultado_pagamento.get(
                'status',
                ''
            )

            if not status_mp:

                messages.error(
                    request,
                    'Mercado Pago não retornou status do pagamento.'
                )

                return redirect('checkout')

            payment_id = str(
                resultado_pagamento.get(
                    'id',
                    ''
                )
            )

            bandeira_cartao = resultado_pagamento.get(
                'bandeira_cartao',
                ''
            )

            if status_mp == 'error':

                messages.error(
                    request,
                    'Erro ao processar pagamento.'
                )

                return redirect('checkout')

            print(
                f"MP PAYMENT ID={payment_id} "
                f"STATUS={status_mp} "
                f"BANDEIRA={bandeira_cartao}"
            )

            if status_mp == 'approved':

                status_pedido = 'PAGO'

            elif status_mp == 'pending':

                status_pedido = 'AGUARDANDO_PAGAMENTO'

            elif status_mp == 'rejected':

                status_pedido = 'CANCELADO'

            elif status_mp in (
                'cancelled',
                'cancelled_by_user',
                'charged_back'
            ):

                status_pedido = 'CANCELADO'

# =========================
        # ✅ PIX
        # =========================
        elif metodo_pagamento == 'pix':

            resultado_pagamento = criar_pagamento_pix(
                valor=total + frete,
                email=request.user.email,
                nome=request.user.get_full_name(),
                cpf=cpf
            )

            print("========== PIX ==========")
            print(resultado_pagamento)
            print("=========================")

            if resultado_pagamento is None:

                messages.error(
                    request,
                    'Erro ao gerar PIX.'
                )

                return redirect('checkout')

            if resultado_pagamento.get(
                'http_status'
            ) != 201:

                messages.error(
                    request,
                    resultado_pagamento.get(
                        'message',
                        'Erro ao gerar PIX.'
                    )
                )

                return redirect('checkout')

            status_mp = resultado_pagamento.get(
                'status',
                ''
            )

            payment_id = str(
                resultado_pagamento.get(
                    'id',
                    ''
                )
            )

            print(
                f"PIX PAYMENT ID={payment_id} "
                f"STATUS={status_mp}"
            )

            if status_mp == 'approved':

                status_pedido = 'PAGO'

            elif status_mp == 'pending':

                status_pedido = 'AGUARDANDO_PAGAMENTO'

            elif status_mp == 'rejected':

                status_pedido = 'CANCELADO'

            elif status_mp in (
                'cancelled',
                'cancelled_by_user',
                'charged_back'
            ):

                status_pedido = 'CANCELADO'
                
# =========================
        # ✅ CRIA PEDIDO
        # =========================

        qr_code = ''

        qr_code_base64 = ''

        if resultado_pagamento:

            qr_code = resultado_pagamento.get(
                'qr_code',
                ''
            )

            qr_code_base64 = resultado_pagamento.get(
                'qr_code_base64',
                ''
            )

        pedido = Pedido.objects.create(
            usuario=request.user,
            codigo=gerar_codigo_pedido(),

            subtotal=total,
            frete=frete,
            total=total + frete,

            status=status_pedido,

            metodo_pagamento=request.POST.get(
                'metodo_pagamento',
                ''
            ),

            mercadopago_payment_id=payment_id,

            mercadopago_status=status_mp,

            bandeira_cartao=bandeira_cartao,

            pix_qr_code=qr_code,

            pix_qr_code_base64=qr_code_base64,

            cpf=cpf,

            frete_nome=request.POST.get(
                'frete_nome',
                ''
            ),

            frete_prazo=request.POST.get(
                'frete_prazo',
                ''
            ),

            nome=request.user.get_full_name(),

            email=request.user.email,

            telefone=(
                endereco_principal.telefone
                if endereco_principal
                else ''
            ),

            cep=(
                endereco_principal.cep
                if endereco_principal
                else ''
            ),

            endereco=(
                endereco_principal.endereco
                if endereco_principal
                else ''
            ),

            numero=(
                endereco_principal.numero
                if endereco_principal
                else ''
            ),

            complemento=(
                endereco_principal.complemento
                if endereco_principal
                else ''
            ),

            cidade=(
                endereco_principal.cidade
                if endereco_principal
                else ''
            ),

            estado=(
                endereco_principal.estado
                if endereco_principal
                else ''
            ),
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

from apps.pagamentos.services import consultar_pagamento


@login_required
def detalhe_pedido(request, codigo):

    pedido = Pedido.objects.filter(
        usuario=request.user,
        codigo=codigo
    ).first()

    if not pedido:

        return redirect('minha_conta')

    # =========================
    # ✅ SINCRONIZA STATUS PIX
    # =========================
    if (
        pedido.mercadopago_payment_id
        and pedido.status == 'AGUARDANDO_PAGAMENTO'
    ):

        try:

            resultado = consultar_pagamento(
                pedido.mercadopago_payment_id
            )

            status_mp = resultado.get(
                'status',
                ''
            )

            if status_mp:

                pedido.mercadopago_status = status_mp

                if status_mp == 'approved':

                    pedido.status = 'PAGO'

                elif status_mp == 'pending':

                    pedido.status = 'AGUARDANDO_PAGAMENTO'

                elif status_mp in (
                    'rejected',
                    'cancelled',
                    'cancelled_by_user',
                    'charged_back'
                ):

                    pedido.status = 'CANCELADO'

                pedido.save()

        except Exception as erro:

            print(
                f'Erro ao consultar Mercado Pago: {erro}'
            )

    return render(
        request,
        'pedidos/detalhe_pedido.html',
        {
            'pedido': pedido,
            'itens': pedido.itens.select_related('perfume')
        }
    )