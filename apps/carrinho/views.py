from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse

from .models import Item
from .utils import get_carrinho

from apps.produtos.models import Perfume, Preco

MAX_QTD = 10


# =========================
# ✅ ADICIONAR AO CARRINHO
# =========================
def adicionar_carrinho(request):
    if request.method == 'POST':
        try:
            perfume_id = request.POST.get('perfume_id')
            preco_id = request.POST.get('preco_id')

            quantidade = int(request.POST.get('quantidade', 1))

            perfume = get_object_or_404(Perfume, id=perfume_id)
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

            limitado = False

            if item:
                nova_qtd = item.quantidade + quantidade

                if nova_qtd > MAX_QTD:
                    nova_qtd = MAX_QTD
                    limitado = True

                item.quantidade = nova_qtd
                item.save()

            else:
                if quantidade > MAX_QTD:
                    quantidade = MAX_QTD
                    limitado = True

                item = Item.objects.create(
                    carrinho=carrinho,
                    perfume=perfume,
                    preco_obj=preco_obj,
                    tamanho=preco_obj.tamanho,
                    preco=preco_obj.valor,
                    quantidade=quantidade
                )

            itens = carrinho.itens.all()

            quantidade_total = sum(i.quantidade for i in itens)
            total = sum(float(i.preco) * i.quantidade for i in itens)

            return JsonResponse({
                "success": True,
                "produto_nome": perfume.nome,
                "tamanho": preco_obj.tamanho,
                "imagem": perfume.imagem.url if perfume.imagem else "",
                "quantidade_total": quantidade_total,
                "total": total,
                "produto_preco": float(preco_obj.valor),
                "quantidade_adicionada": quantidade,
                "limitado": limitado
            })

        except Exception as e:
            print("ERRO CARRINHO:", str(e))

            return JsonResponse({
                "success": False,
                "erro": str(e)
            }, status=500)

    return JsonResponse({"success": False})


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
            quantidade = int(request.POST.get("quantidade"))
        except:
            quantidade = 1

        item = get_object_or_404(Item, id=item_id)
        carrinho = item.carrinho

        if quantidade > 0:

            if quantidade > MAX_QTD:
                quantidade = MAX_QTD

            item.quantidade = quantidade
            item.save()

        else:
            item.delete()

            itens = carrinho.itens.all()
            total = sum(i.preco * i.quantidade for i in itens)
            quantidade_total = sum(i.quantidade for i in itens)

            return JsonResponse({
                "success": True,
                "removido": True,
                "total": float(total),
                "quantidade_total": quantidade_total
            })

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