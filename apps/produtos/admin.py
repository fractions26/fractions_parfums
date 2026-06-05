from django.contrib import admin
from .models import Categoria, Perfume, Preco


# ✅ CATEGORIA
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}


# ✅ INLINE DE PREÇO
class PrecoInline(admin.TabularInline):
    model = Preco
    extra = 1


# ✅ PERFUME
@admin.register(Perfume)
class PerfumeAdmin(admin.ModelAdmin):

    list_display = ("nome", "marca", "mostrar_categorias")

    list_filter = ("categorias",)

    search_fields = ("nome", "marca")

    prepopulated_fields = {"slug": ("nome",)}

    inlines = [PrecoInline]

    filter_horizontal = ("categorias",)

    fields = (
        "nome",
        "marca",
        "slug",
        "categorias",

        "imagem",
        "imagem_mobile",

        "imagem_descricao",
        "imagem_descricao_mobile",
    )

    def mostrar_categorias(self, obj):
        return ", ".join([c.nome for c in obj.categorias.all()])

    mostrar_categorias.short_description = "Categorias"


# ✅ PREÇO
@admin.register(Preco)
class PrecoAdmin(admin.ModelAdmin):
    list_display = ("perfume", "tamanho", "valor")