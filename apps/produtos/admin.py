from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Perfume,
    Categoria,
    Preco,
    Avaliacao
)


# ✅ INLINE DE PREÇO
class PrecoInline(admin.TabularInline):
    model = Preco
    extra = 1


# ✅ CATEGORIA
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}


# ✅ PERFUME
@admin.register(Perfume)
class PerfumeAdmin(admin.ModelAdmin):

    list_display = (
        "nome",
        "marca",
        "estoque_ml",
        "ativo",
        "mostrar_categorias",
        "imagem_preview",
    )

    list_filter = (
        "categorias",
        "ativo",
    )

    search_fields = (
        "nome",
        "marca"
    )

    prepopulated_fields = {
        "slug": ("nome",)
    }

    inlines = [PrecoInline]

    filter_horizontal = (
        "categorias",
    )

    fields = (
        "nome",
        "marca",
        "slug",
        "estoque_ml",
        "ativo",
        "categorias",
        "imagem",
        "imagem_preview",
        "imagem_descricao",
    )

    readonly_fields = (
        "imagem_preview",
    )

    def mostrar_categorias(self, obj):
        return ", ".join(
            [c.nome for c in obj.categorias.all()]
        )

    mostrar_categorias.short_description = "Categorias"

    def imagem_preview(self, obj):

        if obj.imagem:

            return format_html(
                '<img src="{}" style="max-width: 120px; border-radius: 8px;" />',
                obj.get_imagem_url()
            )

        return "Sem imagem"

    imagem_preview.short_description = "Preview"


# ✅ PREÇO
@admin.register(Preco)
class PrecoAdmin(admin.ModelAdmin):

    list_display = (
        "perfume",
        "tamanho",
        "valor"
    )


# ✅ AVALIAÇÕES
@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):

    list_display = (
        "perfume",
        "usuario",
        "nota",
        "aprovado",
        "criado_em"
    )

    list_filter = (
        "nota",
        "aprovado",
        "criado_em"
    )

    search_fields = (
        "perfume__nome",
        "usuario__username",
        "comentario"
    )

    ordering = (
        "-criado_em",
    )
