from decimal import Decimal
import re
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
import requests
from apps.carrinho.utils import get_carrinho
from apps.usuarios.models import Endereco
from .models import Pedido
from .models import ItemPedido
from .services import gerar_codigo_pedido
from decimal import Decimal


# ✅ NOVO: usa decorator (mas mantém seu fluxo)
@login_required(login_url='login')
def checkout(request):

    # ✅ (MANTIDO) fallback antigo ainda preservado
    if not request.user.is_authenticated:
        return redirect(f"{reverse('criar_conta')}?next={request.path}")

    # ✅ CARRINHO (PATCH seguro)
    carrinho = get_carrinho(request)

    if not carrinho or not hasattr(carrinho, 'itens'):
        messages.warning(request, "Seu carrinho está vazio.")
        return redirect('carrinho')

    itens = carrinho.itens.select_related('perfume')

    if not itens.exists():
        messages.warning(request, "Seu carrinho está vazio.")
        return redirect('home')

    # ✅ ENDEREÇO PRINCIPAL
    endereco_principal = Endereco.objects.filter(
        usuario=request.user,
        principal=True
    ).first()

    # ✅ TOTAL (PATCH seguro)
    total = sum(
        (item.preco or 0) * (item.quantidade or 0)
        for item in itens
    )

    # ✅ CRIA PEDIDO
    if request.method == 'POST':

# =====================================
# ✅ CPF (VERSÃO SEGURA)
# =====================================

        perfil = getattr(request.user, 'perfil', None)

        cpf_input = request.POST.get('cpf_pagamento')

        cpf = cpf_input or (perfil.cpf if perfil else '')
        cpf = re.sub(r'\D', '', cpf)


        # =====================================
        # ✅ salva no perfil (apenas se ainda não tiver)
        # =====================================

        if perfil:
            if cpf and not getattr(perfil, 'cpf', None):
                perfil.cpf = cpf
                perfil.save()

        # ✅ FRETE DINÂMICO (PATCH seguro)
        frete_valor = request.POST.get('frete_valor') or '0'

        try:
            frete = Decimal(frete_valor)
        except:
            frete = Decimal('0')

        # ✅ VALIDAÇÃO (não quebra fluxo)
        if frete <= 0:
            messages.warning(request, "Selecione um frete.")
            return redirect('checkout')

        pedido = Pedido.objects.create(

            usuario=request.user,

            codigo=gerar_codigo_pedido(),

            subtotal=total,

            frete=frete,

            # ✅ CPF SALVO NO PEDIDO
            cpf=cpf,

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

                perfume=item.perfume,

                produto_nome=item.perfume.nome,

                tamanho=item.tamanho,

                quantidade=item.quantidade,

                preco=item.preco,

                subtotal=(item.preco * item.quantidade)
            )

        # ✅ LIMPA CARRINHO (MANTIDO)
        itens.delete()
        
        
        # ✅ MENSAGEM DE SUCESSO
        from django.contrib import messages
        messages.success(
            request,
            f"✅ Pedido #{pedido.codigo} realizado com sucesso!"
        )

        # ✅ REDIRECIONA PARA DETALHE DO PEDIDO (RECOMENDADO)
        return redirect('detalhe_pedido', codigo=pedido.codigo)


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