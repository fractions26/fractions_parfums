from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from apps.entrega.utils import possui_frete_gratis
from apps.cupons.models import Cupom
from django.utils import timezone
import json

import requests
import re

from decimal import Decimal
from apps.logs.models import PedidoLog
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.logs.models import CheckoutVisitado
from apps.carrinho.utils import get_carrinho
from apps.usuarios.models import Endereco

from .models import Pedido, ItemPedido
from .services import (
    gerar_codigo_pedido,
    baixar_estoque_pedido
)

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

# =========================
    # ✅ REGISTRA VISITA CHECKOUT
    # =========================

    if request.method == 'GET':

        checkouts = (
            CheckoutVisitado.objects
            .filter(
                usuario=request.user,
                processado=False
            )
            .order_by('-checkout_em')
        )

        checkout = checkouts.first()

        # ✅ Remove registros duplicados antigos
        if checkout and checkouts.count() > 1:

            checkouts.exclude(
                id=checkout.id
            ).delete()

        if checkout:

            checkout.valor_total = total
            checkout.quantidade_itens = itens.count()

            checkout.save()

        else:

            CheckoutVisitado.objects.create(
                usuario=request.user,
                valor_total=total,
                quantidade_itens=itens.count(),
                processado=False
            )

    # =====================================
    # ✅ POST (FINALIZAR PEDIDO)
    # =====================================
    if request.method == 'POST':


        # print("=" * 80)
        # print("POST RECEBIDO")
        # print(dict(request.POST))
        # print("=" * 80)

        # =========================
        # ✅ CPF (OBRIGATÓRIO)
        # =========================
        perfil = getattr(request.user, 'perfil', None)

        cpf_cartao = request.POST.get(
            'cpf_pagamento',
            ''
        ).strip()

        cpf_pix = request.POST.get(
            'cpf_pagamento_pix',
            ''
        ).strip()

        cpf_perfil = (
            perfil.cpf
            if perfil and getattr(perfil, 'cpf', None)
            else ''
        )

        cpf = cpf_cartao or cpf_pix or cpf_perfil

        if not cpf:
            messages.error(
                request,
                "❌ Informe o CPF para continuar."
            )
            return redirect('checkout')

        cpf = re.sub(r'\D', '', str(cpf))

        if len(cpf) != 11:
            messages.error(
                request,
                "❌ CPF inválido."
            )
            return redirect('checkout')

        # ✅ Salva automaticamente nos dados pessoais
        if (
            perfil
            and cpf
            and not getattr(perfil, 'cpf', None)
        ):

            perfil.cpf = cpf
            perfil.save()

        # ✅ GARANTE ENDEREÇO DE ENTREGA
        if not endereco_principal:

            messages.error(
                request,
                "Endereço de entrega não encontrado."
            )

            return redirect(
                'checkout'
            )


        # =========================
        # ✅ FRETE
        # =========================
        frete_valor = request.POST.get(
            'frete_valor'
        ) or '0'

        try:

            frete = Decimal(
                frete_valor
            )

        except Exception:

            frete = Decimal('0')

        frete_gratis = possui_frete_gratis(
            total,
            endereco_principal.cep
        )

        # ✅ Não aceita frete negativo
        if frete < 0:

            messages.warning(
                request,
                "Valor de frete inválido."
            )

            return redirect(
                'checkout'
            )

        # ✅ Força frete zero quando elegível
        if frete_gratis:

            frete = Decimal('0')

        # ✅ Exige frete para quem não tem direito
        elif frete == 0:

            messages.warning(
                request,
                "Selecione um frete."
            )

            return redirect(
                'checkout'
            )
            
        # =========================
        # ✅ CUPOM
        # =========================

        desconto = Decimal('0')

        cupom_codigo = request.POST.get(
            'cupom_codigo',
            ''
        ).strip().upper()

        if cupom_codigo:

            cupom = Cupom.objects.filter(
                codigo=cupom_codigo,
                ativo=True
            ).first()

            if cupom:

                agora = timezone.now()

                cupom_valido = True

                # ✅ Data início
                if (
                    cupom.data_inicio
                    and agora < cupom.data_inicio
                ):

                    cupom_valido = False

                # ✅ Data fim
                if (
                    cupom.data_fim
                    and agora > cupom.data_fim
                ):

                    cupom_valido = False

                # ✅ Primeira compra
                if cupom.primeira_compra:

                    possui_pedido = Pedido.objects.filter(
                        usuario=request.user
                    ).exclude(
                        status='CANCELADO'
                    ).exists()

                    if possui_pedido:

                        cupom_valido = False

                if cupom_valido:

                    desconto = (
                        Decimal(total)
                        *
                        cupom.desconto_percentual
                    ) / Decimal('100')

                else:

                    cupom_codigo = ''

        # =========================
        # ✅ TOTAL BASE
        # =========================

        valor_total = max(
            Decimal('0.01'),
            total + frete - desconto
        )

        # =========================
        # ✅ PAGAMENTO MP
        # =========================
        resultado_pagamento = None

        status_mp = ''

        payment_id = ''

        bandeira_cartao = ''

        status_pedido = 'PENDENTE'

        parcelas = 1

        metodo_pagamento = request.POST.get(
            'metodo_pagamento'
        )

        # print(
        #     "METODO RECEBIDO:",
        #     metodo_pagamento
        # )

        # =========================
        # ✅ CARTÃO DE CRÉDITO
        # =========================
        if metodo_pagamento == 'novo_cartao':
            
            card_token = request.POST.get(
                'card_token'
            )

            parcelas = request.POST.get(
                'parcelas'
            ) or '1'

            payment_method_id = request.POST.get(
                'payment_method_id',
                'visa'
            )

            print(
                'BANDEIRA RECEBIDA:',
                payment_method_id
            )
            
            

            # print("=" * 80)
            # print("METODO:", metodo_pagamento)
            # print("CARD TOKEN:", card_token)
            # print("BANDEIRA:", payment_method_id)
            # print("PARCELAS:", parcelas)
            # print("=" * 80)

            if not card_token:

                messages.error(
                    request,
                    'Token do cartão não recebido.'
                )

                return redirect('checkout')

            resultado_pagamento = criar_pagamento_cartao(
                token=card_token,
                valor=valor_total,
                email=request.user.email,
                nome=request.user.get_full_name(),
                cpf=cpf,
                installments=parcelas,
                payment_method_id=payment_method_id
            )

            if resultado_pagamento is None:

                messages.error(
                    request,
                    'Erro ao processar pagamento.'
                )

                return redirect('checkout')

            if resultado_pagamento.get(
                'http_status'
            ) != 201:

                messages.error(
                    request,
                    resultado_pagamento.get(
                        'message',
                        'Erro ao processar pagamento.'
                    )
                )

                return redirect(
                    'checkout'
                )

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

            # print(
            #     f"MP PAYMENT ID={payment_id} "
            #     f"STATUS={status_mp} "
            #     f"BANDEIRA={bandeira_cartao}"
            # )

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

            # ✅ DESCONTO EXTRA 3% PIX
            desconto_pix = (
                valor_total *
                Decimal('0.03')
            ).quantize(
                Decimal('0.01')
            )

            desconto += desconto_pix

            # ✅ TOTAL FINAL ARREDONDADO PARA 2 CASAS
            valor_total = (
                total +
                frete -
                desconto
            ).quantize(
                Decimal('0.01')
            )

            valor_total = max(
                Decimal('0.01'),
                valor_total
            )

            resultado_pagamento = criar_pagamento_pix(
                valor=valor_total,
                email=request.user.email,
                nome=request.user.get_full_name(),
                cpf=cpf
            )

            # print("RESULTADO PIX:")
            # print(resultado_pagamento)

            if resultado_pagamento is None:

                messages.error(
                    request,
                    'Erro ao gerar PIX.'
                )

                return redirect(
                    'checkout'
                )

            # print(
            #     f"PIX PAYMENT ID={resultado_pagamento.get('id')} "
            #     f"STATUS={resultado_pagamento.get('status')}"
            # )

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

                return redirect(
                    'checkout'
                )

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

            # print(
            #     f"PIX PAYMENT ID={payment_id} "
            #     f"STATUS={status_mp}"
            # )

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

            desconto=desconto,

            cupom_codigo=cupom_codigo,

            total=valor_total,

            status=status_pedido,

            metodo_pagamento=request.POST.get(
                'metodo_pagamento',
                ''
            ),

            parcelas=int(parcelas),

            mercadopago_payment_id=payment_id,

            mercadopago_status=status_mp,

            mercadopago_resposta=(
                json.dumps(
                    resultado_pagamento,
                    ensure_ascii=False
                )
                if resultado_pagamento
                else ''
            ),

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
        
        # ✅ LOG PEDIDO

        PedidoLog.objects.create(
            pedido_id=pedido.id,
            codigo_pedido=pedido.codigo,
            usuario=request.user,
            evento='PEDIDO_CRIADO',
            observacao=(
                f'Status={status_pedido} | '
                f'Pagamento={metodo_pagamento}'
            )
        )

        CheckoutVisitado.objects.filter(
            usuario=request.user,
            processado=False
        ).update(
            processado=True
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
        # ✅ EMAIL CONFIRMAÇÃO PEDIDO
        # =========================

        if pedido.status in (
            'PAGO',
            'AGUARDANDO_PAGAMENTO'
        ):

            try:

                html_content = render_to_string(
                    'emails/pedido_confirmado.html',
                    {
                        'pedido': pedido,
                        'itens': pedido.itens.all(),
                        'nome': pedido.nome,
                    }
                )

                email_msg = EmailMultiAlternatives(

                    subject=(
                        f'✅ Pedido #{pedido.codigo} confirmado'
                    ),

                    body=(
                        f'Seu pedido #{pedido.codigo} foi recebido.'
                    ),

                    from_email=(
                        'Fractions Parfums '
                        '<contato@fractionsparfums.com.br>'
                    ),

                    to=[pedido.email]
                )

                email_msg.attach_alternative(
                    html_content,
                    "text/html"
                )

                email_msg.send()

            except Exception as e:

                print(
                    'Erro ao enviar email do pedido:',
                    e
                )

        # =========================
        # ✅ BAIXA ESTOQUE
        # =========================

        if pedido.status == 'PAGO':

            baixar_estoque_pedido(pedido)

            PedidoLog.objects.create(
                pedido_id=pedido.id,
                codigo_pedido=pedido.codigo,
                usuario=request.user,
                evento='ESTOQUE_BAIXADO',
                observacao='Estoque atualizado'
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

        return redirect(
            'detalhe_pedido',
            codigo=pedido.codigo
        )


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

                status_anterior = pedido.status

                if status_mp == 'approved':
                    
                    pedido.status = 'PAGO'

                    baixar_estoque_pedido(pedido)

                    PedidoLog.objects.create(
                        pedido_id=pedido.id,
                        codigo_pedido=pedido.codigo,
                        usuario=pedido.usuario,
                        evento='ESTOQUE_BAIXADO',
                        observacao='Estoque atualizado após confirmação PIX'
                    )

                    if (
                        status_anterior != 'PAGO'
                        and not pedido.email_pagamento_enviado
                    ):

                        PedidoLog.objects.create(
                            pedido_id=pedido.id,
                            codigo_pedido=pedido.codigo,
                            usuario=pedido.usuario,
                            evento='PAGAMENTO_CONFIRMADO',
                            observacao=(
                                f'MercadoPago={pedido.mercadopago_payment_id}'
                            )
                        )

                        try:

                            html_content = render_to_string(
                                'emails/pagamento_confirmado.html',
                                {
                                    'pedido': pedido
                                }
                            )

                            email_msg = EmailMultiAlternatives(

                                subject=(
                                    f'✅ Pagamento confirmado '
                                    f'#{pedido.codigo}'
                                ),

                                body=(
                                    f'Seu pagamento do pedido '
                                    f'#{pedido.codigo} foi confirmado.'
                                ),

                                from_email=(
                                    'Fractions Parfums '
                                    '<contato@fractionsparfums.com.br>'
                                ),

                                to=[pedido.email]
                            )

                            email_msg.attach_alternative(
                                html_content,
                                "text/html"
                            )

                            email_msg.send()

                            pedido.email_pagamento_enviado = True

                            PedidoLog.objects.create(
                                pedido_id=pedido.id,
                                codigo_pedido=pedido.codigo,
                                usuario=pedido.usuario,
                                evento='EMAIL_PAGAMENTO_ENVIADO',
                                observacao='Email enviado com sucesso'
                            )

                        except Exception as erro:

                            PedidoLog.objects.create(
                                pedido_id=pedido.id,
                                codigo_pedido=pedido.codigo,
                                usuario=pedido.usuario,
                                evento='ERRO_EMAIL_PAGAMENTO',
                                observacao=str(erro)
                            )

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