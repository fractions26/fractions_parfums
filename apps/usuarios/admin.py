from django.contrib import admin

from .models import Endereco


@admin.register(Endereco)
class EnderecoAdmin(admin.ModelAdmin):

    list_display = (
        'usuario',
        'cidade',
        'estado',
        'principal',
    )

    search_fields = (
        'usuario__username',
        'cidade',
        'cpf',
    )

    list_filter = (
        'estado',
        'principal',
    )