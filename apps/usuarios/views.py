from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Endereco


@login_required
def meus_enderecos(request):

    enderecos = Endereco.objects.filter(
        usuario=request.user
    ).order_by('-principal')

    return render(
        request,
        'usuarios/meus_enderecos.html',
        {
            'enderecos': enderecos
        }
    )