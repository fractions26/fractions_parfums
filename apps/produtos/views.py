from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min
from .models import Perfume, Categoria
from django.views.decorators.csrf import ensure_csrf_cookie
from decimal import Decimal
from django.http import JsonResponse

# =========================
# ✅ DETALHE DO PRODUTO
# =========================
def detalhe_produto(request, slug):

    perfume = get_object_or_404(
        Perfume,
        slug=slug
    )

    # ✅ TESTE
    for preco in perfume.precos.all():

        preco.unidades_disponiveis = 99

    return render(
        request,
        'produtos/detalhe.html',
        {
            'perfume': perfume
        }
    )

# =========================
# ✅ LISTA POR CATEGORIA
# =========================
@ensure_csrf_cookie
def lista_categoria(request, slug):

    categorias_param = request.GET.getlist("categoria")

    # ✅ categoria visual
    categoria = get_object_or_404(
        Categoria,
        slug=slug
    )

    perfumes = Perfume.objects.all().annotate(
        menor_preco=Min('precos__valor')
    )

    # =========================
    # ✅ CATEGORIA PADRÃO URL
    # =========================

    if not categorias_param:

        perfumes = perfumes.filter(
            categorias__slug=slug
        )

        categorias_param = [slug]

    # =========================
    # ✅ NOVA REGRA CATEGORIAS
    # =========================

    if categorias_param:

        # ✅ Masculinos + Femininos
        # mostra TODOS sem exceção
        if (
            'masculinos' in categorias_param and
            'femininos' in categorias_param
        ):

            perfumes = perfumes.all()

        # ✅ Arabes + Masculinos
        elif (
            'arabes' in categorias_param and
            'masculinos' in categorias_param
        ):

            perfumes = perfumes.filter(
                categorias__slug='arabes'
            ).filter(
                categorias__slug='masculinos'
            )

        # ✅ Arabes + Femininos
        elif (
            'arabes' in categorias_param and
            'femininos' in categorias_param
        ):

            perfumes = perfumes.filter(
                categorias__slug='arabes'
            ).filter(
                categorias__slug='femininos'
            )

        # ✅ Apenas Arabes
        elif categorias_param == ['arabes']:

            perfumes = perfumes.filter(
                categorias__slug='arabes'
            )

        # ✅ Apenas Masculinos
        elif categorias_param == ['masculinos']:

            perfumes = perfumes.filter(
                categorias__slug='masculinos'
            )

        # ✅ Apenas Femininos
        elif categorias_param == ['femininos']:

            perfumes = perfumes.filter(
                categorias__slug='femininos'
            )

        else:
            
            # ✅ só aplica categoria da URL
            # quando NÃO houver outros filtros
            if not (
                request.GET.getlist('marca') or
                request.GET.getlist('destaque') or
                request.GET.get('q') or
                request.GET.get('preco_min') or
                request.GET.get('preco_max')
            ):

                perfumes = perfumes.filter(
                    categorias__slug=slug
                )

                categorias_param = [slug]

            else:

                # ✅ evita ficar preso na categoria da URL
                categorias_param = []

    # =========================
    # ✅ FILTROS
    # =========================

    marcas = request.GET.getlist('marca')

    destaques = request.GET.getlist('destaque')

    ordenar = request.GET.get('ordenar')

    preco_min = request.GET.get('preco_min')
    preco_max = request.GET.get('preco_max')

    busca = request.GET.get('q')

    # =========================
    # ✅ BUSCA
    # =========================

    if busca:

        perfumes = perfumes.filter(
            Q(nome__icontains=busca) |
            Q(marca__icontains=busca)
        )

    # =========================
    # ✅ MARCAS
    # =========================

    if marcas:

        query = Q()

        for marca in marcas:

            query |= Q(
                marca__icontains=marca.strip()
            )

        perfumes = perfumes.filter(query)

    # =========================
    # ✅ PREÇO
    # =========================

    if preco_min:

        perfumes = perfumes.filter(
            menor_preco__gte=preco_min
        )

    if preco_max:

        perfumes = perfumes.filter(
            menor_preco__lte=preco_max
        )

    # =========================
    # ✅ DESTAQUES
    # =========================

    if 'novidades' in destaques:

        perfumes = perfumes.order_by('-id')

    # =========================
    # ✅ ORDENAÇÃO
    # =========================

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

    # =========================
    # ✅ PARCELAMENTO
    # =========================

    for perfume in perfumes:

        preco = perfume.precos.first()

        if preco:

            preco.parcela_3x = round(
                preco.valor / 3,
                2
            )

    # =========================
    # ✅ MARCAS
    # =========================

    marcas_lista = Perfume.objects.values_list(
        'marca',
        flat=True
    ).distinct()

    return render(request, 'produtos/lista.html', {

        'categoria': categoria,

        'perfumes': perfumes,

        'marcas': marcas_lista,

        'marcas_selecionadas': marcas,

        'destaques_selecionados': destaques,

        'categorias_selecionadas': categorias_param,

    })

# =========================
# ✅ LISTA GERAL
# =========================
@ensure_csrf_cookie
def lista_produtos(request):

    perfumes = Perfume.objects.all().annotate(
        menor_preco=Min('precos__valor')
    )

    # ✅ NOVO
    categorias_param = request.GET.getlist("categoria")

    marcas = request.GET.getlist('marca')
    destaques = request.GET.getlist('destaque')
    ordenar = request.GET.get('ordenar')
    preco_min = request.GET.get('preco_min')
    preco_max = request.GET.get('preco_max')
    busca = request.GET.get('q')

    # =========================
    # ✅ NOVA REGRA CATEGORIAS
    # =========================

    if categorias_param:

        # ✅ Masculinos + Femininos
        if (
            'masculinos' in categorias_param and
            'femininos' in categorias_param
        ):

            perfumes = perfumes.all()

        # ✅ Arabes + Masculinos
        elif (
            'arabes' in categorias_param and
            'masculinos' in categorias_param
        ):

            perfumes = perfumes.filter(
                categorias__slug='arabes'
            ).filter(
                categorias__slug='masculinos'
            )

        # ✅ Arabes + Femininos
        elif (
            'arabes' in categorias_param and
            'femininos' in categorias_param
        ):

            perfumes = perfumes.filter(
                categorias__slug='arabes'
            ).filter(
                categorias__slug='femininos'
            )

        # ✅ Apenas Arabes
        elif categorias_param == ['arabes']:

            perfumes = perfumes.filter(
                categorias__slug='arabes'
            )

        # ✅ Apenas Masculinos
        elif categorias_param == ['masculinos']:

            perfumes = perfumes.filter(
                categorias__slug='masculinos'
            )

        # ✅ Apenas Femininos
        elif categorias_param == ['femininos']:

            perfumes = perfumes.filter(
                categorias__slug='femininos'
            )

    # =========================
    # ✅ BUSCA
    # =========================

    if busca:

        perfumes = perfumes.filter(
            Q(nome__icontains=busca) |
            Q(marca__icontains=busca)
        )

    # =========================
    # ✅ MARCAS
    # =========================

    if marcas:

        query = Q()

        for marca in marcas:

            query |= Q(
                marca__icontains=marca.strip()
            )

        perfumes = perfumes.filter(query)

    # =========================
    # ✅ PREÇO
    # =========================

    if preco_min:

        perfumes = perfumes.filter(
            menor_preco__gte=preco_min
        )

    if preco_max:

        perfumes = perfumes.filter(
            menor_preco__lte=preco_max
        )

    # =========================
    # ✅ DESTAQUES
    # =========================

    if 'novidades' in destaques:

        perfumes = perfumes.order_by('-id')

    # =========================
    # ✅ ORDENAÇÃO
    # =========================

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

    # =========================
    # ✅ PARCELAMENTO
    # =========================

    for perfume in perfumes:

        preco = perfume.precos.first()

        if preco:

            preco.parcela_3x = round(
                preco.valor / 3,
                2
            )

    # ✅ MARCAS
    marcas_lista = Perfume.objects.values_list(
        'marca',
        flat=True
    ).distinct()

    return render(request, 'produtos/lista.html', {

        'categoria': {
            'nome': 'Todos os produtos'
        },

        'perfumes': perfumes,

        'marcas': marcas_lista,

        'marcas_selecionadas': marcas,

        'destaques_selecionados': destaques,

        # ✅ IMPORTANTE
        'categorias_selecionadas': categorias_param,

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
    

# =========================
# ✅ BUSCA AJAX
# =========================
def busca_ajax(request):

    q = request.GET.get("q", "").strip()

    resultados = []

    if q:

        perfumes = Perfume.objects.filter(

            Q(nome__icontains=q) |
            Q(marca__icontains=q)

        ).distinct()[:6]

        for perfume in perfumes:

            preco = perfume.precos.first()

            resultados.append({

                'nome': perfume.nome,

                'slug': perfume.slug,

                # ✅ CORRIGIDO
                'imagem': (
                    f"/static/{perfume.imagem}"
                    if perfume.imagem
                    else ''
                ),

                'preco': (
                    str(preco.valor)
                    if preco
                    else '0.00'
                )

            })

    return JsonResponse({
        'resultados': resultados
    })