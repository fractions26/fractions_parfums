from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import traceback
from django.shortcuts import render
from .models import Item
from .utils import get_carrinho
from apps.produtos.models import Perfume, Preco
from django.templatetags.static import static
from decimal import Decimal
from apps.logs.models import CheckoutVisitado


MAX_QTD = 10


def adicionar_carrinho(request):
    
    if request.method == 'POST':

        try:

            perfume_id = request.POST.get('perfume_id')

            preco_id = request.POST.get('preco_id')

            try:

                quantidade = int(
                    request.POST.get(
                        'quantidade',
                        1
                    )
                )

            except:

                quantidade = 1

            perfume = get_object_or_404(
                Perfume,
                id=perfume_id
            )

            preco_obj = get_object_or_404(
                Preco,
                id=preco_id,
                perfume=perfume
            )

            carrinho = get_carrinho(request)

            item = Item.objects.filter(
                carrinho=carrinho,
                perfume=perfume,
                preco_obj=preco_obj
            ).first()

            # ✅ ML DO TAMANHO SELECIONADO
            tamanho_ml = int(
                ''.join(
                    filter(
                        str.isdigit,
                        preco_obj.tamanho
                    )
                )
            )

            # ✅ ITEM JÁ EXISTENTE
            qtd_existente = (
                item.quantidade
                if item
                else 0
            )

            # ✅ NOVA QTD DA MESMA VARIAÇÃO
            nova_qtd = (
                qtd_existente + quantidade
            )

            # ✅ REGRA GLOBAL
            if nova_qtd > MAX_QTD:

                return JsonResponse({

                    "success": False,

                    "erro": (
                        f"Limite máximo de "
                        f"{MAX_QTD} unidades "
                        f"por volume."
                    )

                })

            # =========================
            # ✅ ML TOTAL NO CARRINHO
            # =========================

            ml_no_carrinho = 0

            # ✅ TODOS OS CARRINHOS
            itens_perfume = Item.objects.filter(
                perfume=perfume
            )

            for i in itens_perfume:

                try:

                    ml_item = int(
                        ''.join(
                            filter(
                                str.isdigit,
                                i.tamanho
                            )
                        )
                    )

                    ml_no_carrinho += (
                        ml_item * i.quantidade
                    )

                except:

                    pass

            # ✅ REMOVE O ITEM ATUAL
            # PARA EVITAR DUPLICAR
            if item:

                ml_no_carrinho -= (
                    tamanho_ml * item.quantidade
                )

            # ✅ NOVO TOTAL ML
            ml_total = (
                ml_no_carrinho +
                (tamanho_ml * nova_qtd)
            )

            # ✅ BLOQUEIA ESTOQUE TOTAL
            if ml_total > perfume.estoque_ml:

                ml_restante = (
                    perfume.estoque_ml -
                    ml_no_carrinho
                )

                maximo_permitido = max(
                    0,
                    ml_restante // tamanho_ml
                )

                return JsonResponse({

                    "success": False,

                    "erro": (
                        f"Estoque insuficiente. "
                        f"Máximo disponível: "
                        f"{maximo_permitido} unidade(s)."
                    )

                })

            limitado = False

            # ✅ ATUALIZA ITEM
            if item:

                item.quantidade = nova_qtd

                item.save()

            # ✅ CRIA ITEM
            else:

                item = Item.objects.create(

                    carrinho=carrinho,

                    perfume=perfume,

                    preco_obj=preco_obj,

                    tamanho=preco_obj.tamanho,

                    preco=float(preco_obj.valor),

                    quantidade=quantidade
                )

            # =========================
            # ✅ RECALCULAR CARRINHO
            # =========================

            itens = carrinho.itens.all()

            quantidade_total = sum(
                i.quantidade
                for i in itens
            )

            total = sum(
                float(i.preco) * i.quantidade
                for i in itens
            )

            total_formatado = (
                f"{total:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

            # =========================
            # ✅ IMAGEM
            # =========================

            imagem_url = ""

            if perfume.imagem:

                try:

                    imagem_url = perfume.imagem.url

                except Exception:

                    imagem_url = static(
                        perfume.imagem
                    )

# =========================
            # ✅ RECUPERAÇÃO DE CARRINHO
            # =========================

            if request.user.is_authenticated:

                checkout = CheckoutVisitado.objects.filter(
                    usuario=request.user,
                    processado=False
                ).first()

                if checkout:

                    if quantidade_total == 0:

                        checkout.delete()

                    else:

                        checkout.valor_total = Decimal(
                            str(total)
                        )

                        checkout.quantidade_itens = (
                            quantidade_total
                        )

                        checkout.save()

                else:

                    if quantidade_total > 0:

                        CheckoutVisitado.objects.create(
                            usuario=request.user,
                            valor_total=Decimal(
                                str(total)
                            ),
                            quantidade_itens=(
                                quantidade_total
                            )
                        )

            # =========================
            # ✅ RESPOSTA FINAL
            # =========================

            return JsonResponse({

                "success": True,

                "produto_nome": perfume.nome,

                "tamanho": preco_obj.tamanho,

                "imagem": imagem_url,

                "quantidade_total": quantidade_total,

                "total": total,

                "total_formatado": total_formatado,

                "produto_preco": float(preco_obj.valor),

                "quantidade_adicionada": quantidade,

                "limitado": limitado

            })

        except Exception as e:

            print("🚨 ERRO CARRINHO:", str(e))

            traceback.print_exc()

            return JsonResponse({

                "success": False,

                "erro": str(e)

            }, status=500)

    return JsonResponse({
        "success": False
    }, status=400)

# =========================
# ✅ VER CARRINHO
# =========================
def ver_carrinho(request):
    
    carrinho = get_carrinho(request)

    itens = carrinho.itens.all()
    total = sum(item.preco * item.quantidade for item in itens)

    response = render(
        request,
        'carrinho.html',
        {
            'itens': itens,
            'total': total
        }
    )

    response["X-Robots-Tag"] = "noindex, nofollow"

    return response


# =========================
# ✅ DRAWER CARRINHO
# =========================
def drawer_carrinho(request):
    
    carrinho = get_carrinho(request)

    itens = carrinho.itens.all()

    total = sum(
        item.preco * item.quantidade
        for item in itens
    )

    response = render(
        request,
        'partials/carrinho_drawer.html',
        {
            'itens': itens,
            'total': total
        }
    )

    # ✅ Impede indexação pelo Google
    response["X-Robots-Tag"] = (
        "noindex, nofollow, noarchive"
    )

    return response


# =========================
# ✅ ATUALIZAR ITEM
# =========================
def atualizar_item(request):

    if request.method == "POST":

        item_id = request.POST.get("item_id")

        try:

            quantidade = int(
                request.POST.get("quantidade")
            )

        except:

            quantidade = 1

        item = get_object_or_404(
            Item,
            id=item_id
        )

        carrinho = item.carrinho

        perfume = item.perfume

        # ✅ EXTRAI ML DO TAMANHO
        tamanho_ml = int(
            ''.join(
                filter(
                    str.isdigit,
                    item.tamanho
                )
            )
        )

        # =========================
        # ✅ ML TOTAL NO CARRINHO
        # =========================

        ml_no_carrinho = 0

        itens_perfume = Item.objects.filter(
            perfume=perfume
        )

        for i in itens_perfume:

            try:

                ml_item = int(
                    ''.join(
                        filter(
                            str.isdigit,
                            i.tamanho
                        )
                    )
                )

                ml_no_carrinho += (
                    ml_item * i.quantidade
                )

            except:

                pass

        ml_no_carrinho -= (
            tamanho_ml * item.quantidade
        )

        ml_total = (
            ml_no_carrinho +
            (tamanho_ml * quantidade)
        )

        if quantidade > 0:

            if quantidade > MAX_QTD:

                return JsonResponse({

                    "success": False,

                    "erro": (
                        f"Limite máximo de "
                        f"{MAX_QTD} unidades."
                    )

                })

            if ml_total > perfume.estoque_ml:

                ml_restante = (
                    perfume.estoque_ml -
                    ml_no_carrinho
                )

                maximo_permitido = max(
                    0,
                    ml_restante // tamanho_ml
                )

                return JsonResponse({

                    "success": False,

                    "erro": (
                        f"Estoque insuficiente. "
                        f"Máximo disponível: "
                        f"{maximo_permitido} unidade(s)."
                    )

                })

            item.quantidade = quantidade

            item.save()

        else:

            item.delete()

            itens = carrinho.itens.all()

            total = sum(
                i.preco * i.quantidade
                for i in itens
            )

            quantidade_total = sum(
                i.quantidade
                for i in itens
            )

            # =========================
            # ✅ RECUPERAÇÃO DE CARRINHO
            # =========================

            if request.user.is_authenticated:

                checkout = CheckoutVisitado.objects.filter(
                    usuario=request.user,
                    processado=False
                ).first()

                if checkout:
                    
                    if quantidade_total == 0:

                        checkout.delete()

                    else:

                        checkout.valor_total = Decimal(
                            str(total)
                        )

                        checkout.quantidade_itens = (
                            quantidade_total
                        )

                        checkout.save()

            return JsonResponse({

                "success": True,

                "removido": True,

                "total": float(total),

                "quantidade_total": quantidade_total

            })

        itens = carrinho.itens.all()

        total = sum(
            i.preco * i.quantidade
            for i in itens
        )

        quantidade_total = sum(
            i.quantidade
            for i in itens
        )

        # =========================
        # ✅ RECUPERAÇÃO DE CARRINHO
        # =========================

        if request.user.is_authenticated:

            checkout = CheckoutVisitado.objects.filter(
                usuario=request.user,
                processado=False
            ).first()

            if checkout:
                
                if quantidade_total == 0:

                    checkout.delete()

                else:

                    checkout.valor_total = Decimal(
                        str(total)
                    )

                    checkout.quantidade_itens = (
                        quantidade_total
                    )

                    checkout.save()

        return JsonResponse({

            "success": True,

            "quantidade_item": item.quantidade,

            "total": float(total),

            "quantidade_total": quantidade_total

        })

    return JsonResponse({
        "success": False
    })
# =========================
# ✅ REMOVER ITEM
# =========================
def remover_item(request):

    if request.method == "POST":

        item_id = request.POST.get(
            "item_id"
        )

        item = get_object_or_404(
            Item,
            id=item_id
        )

        carrinho = item.carrinho

        item.delete()

        itens = carrinho.itens.all()

        total = sum(
            i.preco * i.quantidade
            for i in itens
        )

        quantidade_total = sum(
            i.quantidade
            for i in itens
        )

        # =========================
        # ✅ RECUPERAÇÃO DE CARRINHO
        # =========================

        if request.user.is_authenticated:

            checkout = CheckoutVisitado.objects.filter(
                usuario=request.user,
                processado=False
            ).first()

            if checkout:
                
                if quantidade_total == 0:

                    checkout.delete()

                else:

                    checkout.valor_total = Decimal(
                        str(total)
                    )

                    checkout.quantidade_itens = (
                        quantidade_total
                    )

                    checkout.save()

        return JsonResponse({

            "success": True,

            "total": float(total),

            "quantidade_total": quantidade_total

        })

    return JsonResponse({
        "success": False
    })


# =========================
# ✅ BADGE (QUANTIDADE)
# =========================
def quantidade_carrinho(request):

    carrinho = get_carrinho(request)

    quantidade = sum(item.quantidade for item in carrinho.itens.all())

    return JsonResponse({
        "quantidade": quantidade
    })

from django.contrib.admin.views.decorators import staff_member_required
from .models import Carrinho


@staff_member_required
def carrinhos_ativos(request):

    carrinhos = (
        Carrinho.objects
        .filter(
            usuario__isnull=False,
            itens__isnull=False
        )
        .select_related("usuario")
        .prefetch_related(
            "itens",
            "itens__perfume"
        )
        .distinct()
    )

    return render(
        request,
        "carrinho/carrinhos_ativos.html",
        {
            "carrinhos": carrinhos
        }
    )