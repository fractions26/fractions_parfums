from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .services import consultar_parcelas


def pagamento(request):

    return render(
        request,
        'pagamentos/pagamento.html'
    )


@login_required
def consultar_parcelas_checkout(request):

    bin_cartao = request.GET.get('bin')
    valor = request.GET.get('valor')

    if not bin_cartao or not valor:

        return JsonResponse({
            'success': False,
            'erro': 'BIN ou valor não informado.'
        })

    resultado = consultar_parcelas(
        bin_cartao,
        valor
    )

    return JsonResponse({
        'success': True,
        'dados': resultado
    })