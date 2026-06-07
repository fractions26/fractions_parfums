from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import traceback
from django.shortcuts import render
from .models import Item
from .utils import get_carrinho
from apps.produtos.models import Perfume, Preco
from django.templatetags.static import static

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

            # ✅ EXTRAI ML DO TAMANHO
            tamanho_ml = int(
                ''.join(
                    filter(
                        str.isdigit,
                        preco_obj.tamanho
                    )
                )
            )

            # ✅ QUANTIDADE ATUAL NO CARRINHO
            qtd_existente = (
                item.quantidade
                if item
                else 0
            )

            # ✅ NOVA QUANTIDADE
            nova_qtd = (
                qtd_existente + quantidade
            )

            # ✅ LIMITE PELO ESTOQUE
            maximo_por_estoque = (
                perfume.estoque_ml // tamanho_ml
            )

            # ✅ REGRA FINAL
            # mantém proteção de no máximo 10 itens
            maximo_permitido = min(
                MAX_QTD,
                maximo_por_estoque
            )

            # ✅ BLOQUEIA ULTRAPASSAR
            if nova_qtd > maximo_permitido:

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

            # ✅ RECALCULAR CARRINHO
            itens = carrinho.itens.all()

            quantidade_total = sum(
                i.quantidade
                for i in itens
            )

            total = sum(
                float(i.preco) * i.quantidade
                for i in itens
            )

            # ✅ FORMATA TOTAL
            total_formatado = (
                f"{total:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

            # ✅ IMAGEM
            imagem_url = ""

            if perfume.imagem:

                try:

                    imagem_url = perfume.imagem.url

                except Exception:

                    imagem_url = static(
                        perfume.imagem
                    )

            # ✅ RESPOSTA FINAL
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

    return render(request, 'carrinho.html', {
        'itens': itens,
        'total': total
    })


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

        # ✅ LIMITE PELO ESTOQUE
        maximo_por_estoque = (
            perfume.estoque_ml // tamanho_ml
        )

        # ✅ REGRA FINAL
        maximo_permitido = min(
            MAX_QTD,
            maximo_por_estoque
        )

        if quantidade > 0:

            # ✅ BLOQUEIA LIMITE
            if quantidade > maximo_permitido:

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

        return JsonResponse({

            "success": True,

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

        item_id = request.POST.get("item_id")

        item = get_object_or_404(Item, id=item_id)
        carrinho = item.carrinho

        item.delete()

        itens = carrinho.itens.all()
        total = sum(i.preco * i.quantidade for i in itens)
        quantidade_total = sum(i.quantidade for i in itens)

        return JsonResponse({
            "success": True,
            "total": float(total),
            "quantidade_total": quantidade_total
        })

    return JsonResponse({"success": False})


# =========================
# ✅ BADGE (QUANTIDADE)
# =========================
def quantidade_carrinho(request):

    carrinho = get_carrinho(request)

    quantidade = sum(item.quantidade for item in carrinho.itens.all())

    return JsonResponse({
        "quantidade": quantidade
    })