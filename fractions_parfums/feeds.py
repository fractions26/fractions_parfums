from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape

from apps.produtos.models import Perfume


def google_shopping_feed(request):

    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">',
        '<channel>',
        '<title>Fractions Parfums</title>',
        '<link>https://www.fractionsparfums.com.br</link>',
        '<description>Decants de perfumes importados originais</description>',
    ]

    perfumes = (
        Perfume.objects
        .filter(ativo=True)
        .prefetch_related("precos", "categorias")
        .order_by("nome")
    )

    for perfume in perfumes:

        # =====================================================
        # PREÇO DO GOOGLE = SEMPRE 2ml
        # =====================================================
        preco = (
            perfume.precos
            .filter(tamanho__icontains="2")
            .order_by("valor")
            .first()
        )

        # Se não existir 2ml utiliza o menor preço disponível
        if not preco:
            preco = (
                perfume.precos
                .order_by("valor")
                .first()
            )

        if not preco:
            continue

        disponibilidade = (
            "in stock"
            if perfume.ativo and perfume.estoque_ml > 0
            else "out of stock"
        )

        categoria = ""

        if perfume.categorias.exists():
            categoria = perfume.categorias.first().nome

        try:
            url_produto = request.build_absolute_uri(
                reverse(
                    "detalhe_produto",
                    args=[perfume.slug]
                )
            )
        except Exception:
            url_produto = (
                f"https://www.fractionsparfums.com.br/produtos/detalhe/{perfume.slug}/"
            )

        imagem = (
            "https://www.fractionsparfums.com.br"
            + perfume.get_imagem_url()
        )

        descricao = (
            f"{perfume.nome} {preco.tamanho}. "
            "Decant de perfume importado, ideal para experimentar a fragrância antes de investir no frasco completo."
        )

        xml.append(f"""
<item>
    <g:id>{perfume.id}</g:id>

    <title><![CDATA[{perfume.nome} {preco.tamanho}]]></title>

    <description><![CDATA[{descricao}]]></description>

    <link>{url_produto}</link>

    <g:image_link>{imagem}</g:image_link>

    <g:availability>{disponibilidade}</g:availability>

    <g:condition>new</g:condition>

    <g:price>{preco.valor} BRL</g:price>

    <g:brand><![CDATA[{escape(perfume.marca)}]]></g:brand>
    
    <g:size>{preco.tamanho}</g:size>

    <g:product_type><![CDATA[{categoria}]]></g:product_type>

    <g:identifier_exists>false</g:identifier_exists>

    <g:google_product_category>4713</g:google_product_category>
</item>
""")

    xml.append("</channel>")
    xml.append("</rss>")

    return HttpResponse(
        "\n".join(xml),
        content_type="application/xml; charset=utf-8"
    )