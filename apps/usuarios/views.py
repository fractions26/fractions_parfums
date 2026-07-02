from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

from .models import Endereco
from apps.logs.models import LoginLog


# =====================================
# ✅ LOGIN
# =====================================
def login_view(request):

    if request.method == 'POST':

        email = request.POST.get('email')
        senha = request.POST.get('senha')

        user = authenticate(
            request,
            username=email,
            password=senha
        )

        if user:

            login(request, user)

            next_url = request.POST.get('next')

            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)

            return redirect('home')

        # ✅ FALHA DE LOGIN
        LoginLog.objects.create(
            email=email,
            evento='LOGIN_FALHA',
            sucesso=False,
            ip=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get(
                'HTTP_USER_AGENT',
                ''
            )
        )

        response = render(
            request,
            'login.html',
            {
                'erro': 'Email ou senha inválidos'
            }
        )

        response["X-Robots-Tag"] = "noindex, nofollow"

        return response

    response = render(
        request,
        'login.html'
    )

    response["X-Robots-Tag"] = "noindex, nofollow"

    return response


# =====================================
# ✅ CRIAR CONTA
# =====================================
def criar_conta(request):

    if request.method == 'POST':

        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip().lower()
        senha = request.POST.get('senha')
        confirmar = request.POST.get('confirmar')

        # ✅ valida nome
        if not nome:

            response = render(request, 'criar_conta.html', {
                'erro': 'Informe seu nome'
            })

            response["X-Robots-Tag"] = "noindex, nofollow"

            return response

        # ✅ valida email
        if not email:

            response = render(request, 'criar_conta.html', {
                'erro': 'Informe seu email'
            })

            response["X-Robots-Tag"] = "noindex, nofollow"

            return response

        # ✅ senha
        if not senha or not confirmar:

            response = render(request, 'criar_conta.html', {
                'erro': 'Preencha a senha corretamente'
            })

            response["X-Robots-Tag"] = "noindex, nofollow"

            return response

        if senha != confirmar:

            response = render(request, 'criar_conta.html', {
                'erro': 'As senhas não coincidem'
            })

            response["X-Robots-Tag"] = "noindex, nofollow"

            return response

        if len(senha) < 8:

            response = render(request, 'criar_conta.html', {
                'erro': 'Senha muito curta (mínimo 8 caracteres)'
            })

            response["X-Robots-Tag"] = "noindex, nofollow"

            return response

        # ✅ evita duplicado
        if User.objects.filter(username__iexact=email).exists():

            response = render(request, 'criar_conta.html', {
                'erro': 'Email já cadastrado'
            })

            response["X-Robots-Tag"] = "noindex, nofollow"

            return response

        user = User.objects.create_user(

            username=email,

            email=email,

            password=senha,

            first_name=first_name,

            last_name=last_name
        )

        # ✅ login automático
        login(
            request,
            user,
            backend='django.contrib.auth.backends.ModelBackend'
        )

        # ✅ redirect seguro (checkout support ✅)
        next_url = request.POST.get('next') or request.GET.get('next')

        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()}
        ):
            return redirect(next_url)

        return redirect('/pedido/')

    response = render(request, 'criar_conta.html')

    response["X-Robots-Tag"] = "noindex, nofollow"

    return response


# =====================================
# ✅ MEUS ENDEREÇOS
# =====================================
@login_required
def meus_enderecos(request):

    endereco = Endereco.objects.filter(
        usuario=request.user,
        principal=True
    ).first()

    if request.method == 'POST':

        dados = {
            'nome_destinatario': request.POST.get('alias'),
            'endereco': request.POST.get('endereco'),
            'numero': request.POST.get('numero'),
            'complemento': request.POST.get('complemento'),
            'bairro': request.POST.get('bairro'),
            'cidade': request.POST.get('cidade'),
            'estado': request.POST.get('estado'),
            'cep': request.POST.get('cep'),
            'telefone': request.POST.get('telefone'),
            'usuario': request.user,
            'principal': True
        }

        if endereco:
            for campo, valor in dados.items():
                setattr(endereco, campo, valor)
            endereco.save()
        else:
            endereco = Endereco.objects.create(**dados)

        # ✅ redirect inteligente (checkout friendly)
        next_url = request.POST.get('next')

        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()}
        ):
            return redirect(next_url)

        return redirect('checkout')

    return render(
        request,
        'usuarios/editar_endereco.html',
        {
            'endereco': endereco
        }
    )