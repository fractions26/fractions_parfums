# ✅ Carrinho
from .models import Carrinho

# ✅ Marcas
from apps.produtos.models import Perfume


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


# ✅ NOVO - MENU DE MARCAS
def marcas_menu(request):

    marcas = Perfume.objects.values_list('marca', flat=True)\
        .exclude(marca__isnull=True)\
        .exclude(marca__exact='')\
        .distinct()\
        .order_by('marca')

    return {
        "marcas_menu": marcas
    }
