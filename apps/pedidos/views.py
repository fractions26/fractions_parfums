from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect

from apps.carrinho.utils import get_carrinho

from .models import Pedido
from .models import ItemPedido

from .services import gerar_codigo_pedido


@login_required
def checkout(request):

    carrinho = get_carrinho(request)

    itens = carrinho.itens.all()

    total = sum(
        item.preco * item.quantidade
        for item in itens
    )

    # ✅ cria pedido
    if request.method == 'POST':

        frete = Decimal('0.00')

        pedido = Pedido.objects.create(

            usuario=request.user,

            codigo=gerar_codigo_pedido(),

            subtotal=total,

            frete=frete,

            total=total + frete,

            nome=request.POST.get('nome'),

            email=request.POST.get('email'),

            telefone=request.POST.get('telefone'),

            cep=request.POST.get('cep'),

            endereco=request.POST.get('endereco'),

            numero=request.POST.get('numero'),

            complemento=request.POST.get('complemento'),

            cidade=request.POST.get('cidade'),

            estado=request.POST.get('estado'),
        )

        # ✅ cria itens do pedido
        for item in itens:

            ItemPedido.objects.create(

                pedido=pedido,

                produto_nome=item.perfume.nome,

                tamanho=item.tamanho,

                quantidade=item.quantidade,

                preco=item.preco,

                subtotal=(
                    item.preco * item.quantidade
                )
            )

        # ✅ limpa carrinho
        itens.delete()

        # ✅ redireciona pagamento
        return redirect('pagamento')

    return render(
        request,
        'pedidos/checkout.html',
        {
            'itens': itens,
            'total': total
        }
    )