from django.contrib import admin

from .models import Carrinho, Item


class ItemInline(admin.TabularInline):
    model = Item
    extra = 0

    readonly_fields = (
        "perfume",
        "tamanho",
        "preco",
        "quantidade"
    )

    can_delete = False


@admin.register(Carrinho)
class CarrinhoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "usuario",
        "email_usuario",
        "qtd_itens",
        "valor_total"
    )

    search_fields = (
        "usuario__username",
        "usuario__email"
    )

    inlines = [ItemInline]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(itens__isnull=False)
            .distinct()
        )

    def email_usuario(self, obj):
        if obj.usuario:
            return obj.usuario.email
        return "-"

    email_usuario.short_description = "Email"

    def qtd_itens(self, obj):
        return sum(
            item.quantidade
            for item in obj.itens.all()
        )

    qtd_itens.short_description = "Itens"

    def valor_total(self, obj):

        total = sum(
            item.preco * item.quantidade
            for item in obj.itens.all()
        )

        return f"R$ {total:.2f}"

    valor_total.short_description = "Total"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):

    list_display = (
        "perfume",
        "carrinho",
        "tamanho",
        "quantidade",
        "preco"
    )

    search_fields = (
        "perfume__nome",
        "carrinho__usuario__email"
    )