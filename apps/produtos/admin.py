from django.contrib import admin
from django.utils.html import format_html
from .models import Perfume, Categoria, Preco


# ✅ INLINE DE PREÇO
class PrecoInline(admin.TabularInline):
    model = Preco
    extra = 1


# ✅ PERFUME
@admin.register(Perfume)
class PerfumeAdmin(admin.ModelAdmin):

    # ✅ LISTAGEM
    list_display = ("nome", "marca", "mostrar_categorias", "imagem_preview")

    list_filter = ("categorias",)

    search_fields = ("nome", "marca")

    prepopulated_fields = {"slug": ("nome",)}

    # ✅ INLINE PREÇO
    inlines = [PrecoInline]

    filter_horizontal = ("categorias",)

    # ✅ ORDEM DOS CAMPOS NO FORM
    fields = (
        "nome",
        "marca",
        "slug",
        "categorias",

        "imagem",
        "imagem_preview",

        "imagem_mobile",
        "imagem_descricao",
        "imagem_descricao_mobile",
    )

    # ✅ CAMPOS SOMENTE LEITURA
    readonly_fields = ("imagem_preview",)

    # ✅ MOSTRAR CATEGORIAS NA LISTA
    def mostrar_categorias(self, obj):
        return ", ".join([c.nome for c in obj.categorias.all()])

    mostrar_categorias.short_description = "Categorias"

    # ✅ PREVIEW DA IMAGEM
    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="max-width: 120px; border-radius: 8px;" />',
                obj.imagem.url
            )
        return "Sem imagem"

    imagem_preview.short_description = "Preview"
