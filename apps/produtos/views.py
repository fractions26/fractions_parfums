from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min
from .models import Perfume, Categoria
from django.views.decorators.csrf import ensure_csrf_cookie
from decimal import Decimal

# ✅ DETALHE DO PRODUTO
def detalhe_produto(request, slug):
    perfume = get_object_or_404(Perfume, slug=slug)
    return render(request, 'produtos/detalhe.html', {'perfume': perfume})


# ✅ LISTA POR CATEGORIA
@ensure_csrf_cookie
def lista_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)

    perfumes = Perfume.objects.filter(categorias__in=[categoria]).annotate(
        menor_preco=Min('precos__valor')
    )

    # ✅ FILTROS
    marcas = request.GET.getlist('marca')
    destaques = request.GET.getlist('destaque')
    ordenar = request.GET.get('ordenar')
    preco_min = request.GET.get('preco_min')
    preco_max = request.GET.get('preco_max')
    busca = request.GET.get('q')

    if busca:
        perfumes = perfumes.filter(
            Q(nome__icontains=busca) |
            Q(marca__icontains=busca)
        )

    if marcas:
        query = Q()
        for marca in marcas:
            query |= Q(marca__icontains=marca.strip())
        perfumes = perfumes.filter(query)

    if preco_min:
        perfumes = perfumes.filter(menor_preco__gte=preco_min)

    if preco_max:
        perfumes = perfumes.filter(menor_preco__lte=preco_max)

    if 'novidades' in destaques:
        perfumes = perfumes.order_by('-id')

    # ✅ ORDENAÇÃO
    if ordenar == 'mais_vendidos':
        perfumes = perfumes.order_by('-id')
    elif ordenar == 'preco_asc':
        perfumes = perfumes.order_by('menor_preco')
    elif ordenar == 'preco_desc':
        perfumes = perfumes.order_by('-menor_preco')
    elif ordenar == 'az':
        perfumes = perfumes.order_by('nome')
    elif ordenar == 'za':
        perfumes = perfumes.order_by('-nome')

    perfumes = perfumes.distinct()

    # ✅ 🔥 CALCULO PARCELAMENTO (CORRETO)
    for perfume in perfumes:
        preco = perfume.precos.first()
        if preco:
            preco.parcela_3x = round(preco.valor / 3, 2)

    marcas_lista = Perfume.objects.values_list('marca', flat=True).distinct()

    return render(request, 'produtos/lista.html', {
        'categoria': categoria,
        'perfumes': perfumes,
        'marcas': marcas_lista,
        'marcas_selecionadas': marcas,
        'destaques_selecionados': destaques,
    })


# ✅ LISTA POR CATEGORIA
@ensure_csrf_cookie
def lista_categoria(request, slug):

    from django.db.models import Q, Min
    from django.shortcuts import get_object_or_404, render

    # ✅ PRIORIDADE: categoria via filtro (GET)
    categoria_param = request.GET.get("categoria")

    if categoria_param:
        categoria = get_object_or_404(Categoria, slug=categoria_param)
    else:
        categoria = get_object_or_404(Categoria, slug=slug)

    # ✅ QUERY BASE (UMA VEZ SÓ)
    perfumes = Perfume.objects.filter(
        categorias__in=[categoria]
    ).annotate(
        menor_preco=Min('precos__valor')
    )

    # ======================
    # ✅ FILTROS
    # ======================
    marcas = request.GET.getlist('marca')
    destaques = request.GET.getlist('destaque')
    ordenar = request.GET.get('ordenar')
    preco_min = request.GET.get('preco_min')
    preco_max = request.GET.get('preco_max')
    busca = request.GET.get('q')

    if busca:
        perfumes = perfumes.filter(
            Q(nome__icontains=busca) |
            Q(marca__icontains=busca)
        )

    if marcas:
        query = Q()
        for marca in marcas:
            query |= Q(marca__icontains=marca.strip())
        perfumes = perfumes.filter(query)

    if preco_min:
        perfumes = perfumes.filter(menor_preco__gte=preco_min)

    if preco_max:
        perfumes = perfumes.filter(menor_preco__lte=preco_max)

    if 'novidades' in destaques:
        perfumes = perfumes.order_by('-id')

    # ======================
    # ✅ ORDENAÇÃO
    # ======================
    if ordenar == 'mais_vendidos':
        perfumes = perfumes.order_by('-id')
    elif ordenar == 'preco_asc':
        perfumes = perfumes.order_by('menor_preco')
    elif ordenar == 'preco_desc':
        perfumes = perfumes.order_by('-menor_preco')
    elif ordenar == 'az':
        perfumes = perfumes.order_by('nome')
    elif ordenar == 'za':
        perfumes = perfumes.order_by('-nome')

    perfumes = perfumes.distinct()

    # ======================
    # ✅ PARCELAMENTO
    # ======================
    for perfume in perfumes:
        preco = perfume.precos.first()
        if preco:
            preco.parcela_3x = round(preco.valor / 3, 2)

    # ======================
    # ✅ LISTA DE MARCAS
    # ======================
    marcas_lista = Perfume.objects.values_list(
        'marca', flat=True
    ).distinct()

    # ======================
    # ✅ RENDER FINAL
    # ======================
    return render(request, 'produtos/lista.html', {
        'categoria': categoria,
        'perfumes': perfumes,
        'marcas': marcas_lista,
        'marcas_selecionadas': marcas,
        'destaques_selecionados': destaques,
    })
    

# =========================
# ✅ DETALHES DE PAGAMENTO
# =========================
def detalhes_pagamento(request, perfume_id):

    perfume = get_object_or_404(Perfume, id=perfume_id)
    preco = perfume.precos.first()

    parcelas = []

    if preco:
        valor = Decimal(preco.valor)

        for i in range(1, 13):
            valor_parcela = (valor / i).quantize(Decimal("0.01"))
            total = (valor_parcela * i).quantize(Decimal("0.01"))

            parcelas.append({
                'vezes': i,
                'parcela': valor_parcela,
                'total': total
            })

    return render(request, 'produtos/detalhes_pagamento.html', {
        'perfume': perfume,
        'preco': preco,
        'parcelas': parcelas
    })