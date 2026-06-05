# ✅ Carrinho
from .models import Carrinho

# ✅ Marcas
from apps.produtos.models import Perfume

from django.db import ProgrammingError
from django.db.utils import OperationalError


def carrinho_quantidade(request):

    quantidade = 0

    if request.session.session_key:

        carrinho = Carrinho.objects.filter(
            session_key=request.session.session_key
        ).first()

        if carrinho:
            quantidade = sum(item.quantidade for item in carrinho.itens.all())

    return {
        "cart_count": quantidade
    }


# ✅ MENU DE MARCAS
def marcas_menu(request):

    try:
        marcas = (
            Perfume.objects.values_list('marca', flat=True)
            .exclude(marca__isnull=True)
            .exclude(marca__exact='')
            .distinct()
            .order_by('marca')
        )

    except (ProgrammingError, OperationalError):
        marcas = []

    return {
        "marcas_menu": marcas
    }