from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .models import Endereco


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

            # ✅ REDIRECIONA PRO DESTINO CERTO
            next_url = request.POST.get('next')

            if next_url:
                return redirect(next_url)

            return redirect('home')

        return render(request, 'login.html', {
            'erro': 'Email ou senha inválidos'
        })

    return render(request, 'login.html')


# =====================================
# ✅ CRIAR CONTA
# =====================================
def criar_conta(request):
    
    if request.method == 'POST':

        nome = request.POST.get('nome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar = request.POST.get('confirmar')

        # ✅ valida senha
        if senha != confirmar:
            return render(request, 'criar_conta.html', {
                'erro': 'As senhas não coincidem'
            })

        # ✅ evita duplicado
        if User.objects.filter(username=email).exists():
            return render(request, 'criar_conta.html', {
                'erro': 'Email já cadastrado'
            })

        # ✅ cria usuario
        user = User.objects.create_user(
            username=email,
            email=email,
            password=senha,
            first_name=nome
        )

        # ✅ LOGA AUTOMATICAMENTE
        login(request, user)

        # ✅ REDIRECIONA COM SEGURANÇA
        next_url = request.POST.get('next') or request.GET.get('next')

        if next_url:
            return redirect(next_url)

        return redirect('/pedido/')

    return render(request, 'criar_conta.html')

# =====================================
# ✅ MEUS ENDEREÇOS
# =====================================
@login_required
def meus_enderecos(request):

    # ✅ BUSCA ENDEREÇO PRINCIPAL
    endereco = Endereco.objects.filter(
        usuario=request.user,
        principal=True
    ).first()

    if request.method == 'POST':

        # ✅ SE JÁ EXISTE → ATUALIZA
        if endereco:

            endereco.nome_destinatario = request.POST.get('alias')
            endereco.endereco = request.POST.get('endereco')
            endereco.numero = request.POST.get('numero')
            endereco.complemento = request.POST.get('complemento')
            endereco.bairro = request.POST.get('bairro')
            endereco.cidade = request.POST.get('cidade')
            endereco.estado = request.POST.get('estado')
            endereco.cep = request.POST.get('cep')
            endereco.telefone = request.POST.get('telefone')

            endereco.save()

        # ✅ SE NÃO EXISTE → CRIA NOVO
        else:

            endereco = Endereco.objects.create(
                usuario=request.user,
                nome_destinatario=request.POST.get('alias'),
                endereco=request.POST.get('endereco'),
                numero=request.POST.get('numero'),
                complemento=request.POST.get('complemento'),
                bairro=request.POST.get('bairro'),
                cidade=request.POST.get('cidade'),
                estado=request.POST.get('estado'),
                cep=request.POST.get('cep'),
                telefone=request.POST.get('telefone'),
                principal=True
            )

        # ✅ REDIRECIONAMENTO INTELIGENTE
        next_url = request.POST.get('next')

        if next_url:
            return redirect(next_url)

        return redirect('checkout')

    # ✅ GET → ENVIA PRA TELA JÁ PREENCHIDO
    return render(
        request,
        'usuarios/editar_endereco.html',
        {
            'endereco': endereco
        }
    )

    

