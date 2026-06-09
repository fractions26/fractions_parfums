import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from apps.produtos.models import Perfume
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from apps.carrinho.models import Carrinho
from apps.carrinho.models import Carrinho, Item
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
import re
from apps.usuarios.models import Endereco
from apps.carrinho.models import Carrinho, Item
from apps.pedidos.models import Pedido



# ✅ 🔥 VINCULAR CARRINHO AO USUÁRIO (COM MIGRAÇÃO DE ITENS)
def vincular_carrinho_usuario(request, user):

    session_key = request.session.session_key

    # ✅ garante session
    if not session_key:
        request.session.save()
        session_key = request.session.session_key

    # 🔹 carrinho atual da sessão
    carrinho_session, _ = Carrinho.objects.get_or_create(
        session_key=session_key
    )

    # 🔹 carrinho já existente do usuário
    carrinho_user = Carrinho.objects.filter(usuario=user).first()

    # ✅ SE JÁ EXISTIR carrinho do usuário → MIGRA ITENS
    if carrinho_user:

        for item in carrinho_session.itens.all():

            item_existente = Item.objects.filter(
                carrinho=carrinho_user,
                perfume=item.perfume,
                preco_obj=item.preco_obj
            ).first()

            if item_existente:
                item_existente.quantidade += item.quantidade
                item_existente.save()
                item.delete()
            else:
                item.carrinho = carrinho_user
                item.save()

        carrinho = carrinho_user

    else:
        carrinho = carrinho_session

    # ✅ vincula carrinho ao usuário
    carrinho.usuario = user
    carrinho.save()


# ✅ HOME
def home(request):
    masculinos = Perfume.objects.filter(categorias__slug='masculinos').distinct()
    femininos = Perfume.objects.filter(categorias__slug='femininos').distinct()

    return render(request, 'home.html', {
        'masculinos': masculinos,
        'femininos': femininos
    })


# ✅ CONTATO
def contato(request):

    if request.method == "POST":

        nome = request.POST.get('nome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        mensagem = request.POST.get('mensagem')

        # ✅ reCAPTCHA
        recaptcha_response = request.POST.get(
            'g-recaptcha-response'
        )

        if not recaptcha_response:

            messages.error(
                request,
                "❌ Confirme que você não é um robô."
            )

            return redirect('contato')

        data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }

        try:

            r = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data=data,
                timeout=5
            )

            result = r.json()

        except requests.exceptions.RequestException:

            messages.error(
                request,
                "⚠️ Serviço de validação indisponível."
            )

            return redirect('contato')

        # ✅ CAPTCHA INVÁLIDO
        if not result.get('success'):

            messages.error(
                request,
                "❌ Confirme que você não é um robô."
            )

            return redirect('contato')

        # ✅ ENVIO EMAIL
        try:

            from django.core.mail import send_mail

            assunto = 'Novo contato - Fractions Parfums'

            corpo = f"""
            Novo contato recebido pelo site.

            Nome: {nome}

            Email: {email}

            Telefone: {telefone}

            Mensagem:

            {mensagem.replace(chr(10), chr(10) * 2)}
            """

            send_mail(
                subject=assunto,
                message=corpo,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )

            messages.success(
                request,
                "✅ Mensagem enviada com sucesso!"
            )

        except Exception as e:

            print("ERRO EMAIL:", e)

            messages.error(
                request,
                "❌ Erro ao enviar mensagem."
            )

        return redirect('contato')

    return render(request, 'contato.html', {

        'RECAPTCHA_SITE_KEY':
            settings.RECAPTCHA_SITE_KEY

    })

def normalizar_nome(nome_completo):
    nome_limpo = " ".join(nome_completo.strip().split())
    palavras = nome_limpo.split()

    palavras = [p.capitalize() for p in palavras]

    first_name = palavras[0] if palavras else ""
    last_name = " ".join(palavras[1:]) if len(palavras) > 1 else ""

    return first_name, last_name


# ✅ CRIAR CONTA
def criar_conta(request):

    if request.method == "POST":

        # ✅ NOME
        nome_completo = request.POST.get(
            'nome',
            ''
        )

        if not nome_completo.strip():

            messages.error(
                request,
                "❌ Informe seu nome completo."
            )

            return redirect('criar_conta')

        if len(nome_completo.split()) < 2:

            messages.error(
                request,
                "❌ Informe nome e sobrenome."
            )

            return redirect('criar_conta')

        first_name, last_name = normalizar_nome(
            nome_completo
        )

        # ✅ DADOS
        email = request.POST.get(
            'email',
            ''
        ).strip().lower()

        telefone = request.POST.get(
            'telefone'
        )

        senha = request.POST.get(
            'senha'
        )

        confirmar = request.POST.get(
            'confirmar'
        )

        recaptcha_response = request.POST.get(
            'g-recaptcha-response'
        )

        # ✅ EMAIL
        if not email:

            messages.error(
                request,
                "❌ Informe seu e-mail."
            )

            return redirect('criar_conta')

        try:

            validate_email(email)

        except ValidationError:

            messages.error(
                request,
                "❌ Informe um e-mail válido."
            )

            return redirect('criar_conta')

        # ✅ CAPTCHA
        if not recaptcha_response:

            messages.error(
                request,
                "❌ Confirme que você não é um robô."
            )

            return redirect('criar_conta')

        data = {

            'secret': settings.RECAPTCHA_SECRET_KEY,

            'response': recaptcha_response
        }

        try:

            r = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data=data,
                timeout=5
            )

            result = r.json()

        except requests.exceptions.RequestException:

            messages.error(
                request,
                "⚠️ Serviço de validação indisponível."
            )

            return redirect('criar_conta')

        if not result.get('success'):

            messages.error(
                request,
                "❌ Confirme que você não é um robô."
            )

            return redirect('criar_conta')

        # ✅ SENHA
        if senha != confirmar:

            messages.error(
                request,
                "❌ As senhas não coincidem."
            )

            return redirect('criar_conta')

        if len(senha) < 8:

            messages.error(
                request,
                "❌ A senha deve ter pelo menos 8 caracteres."
            )

            return redirect('criar_conta')

        if senha.isnumeric():

            messages.error(
                request,
                "❌ A senha não pode conter apenas números."
            )

            return redirect('criar_conta')

        if not any(c.isalpha() for c in senha):

            messages.error(
                request,
                "❌ A senha deve conter pelo menos uma letra."
            )

            return redirect('criar_conta')

        senhas_comuns = [

            "12345678",
            "123456789",
            "1234567",
            "123456",
            "password",
            "senha",
            "senha123",
            "admin",
            "teste123"
        ]

        if senha.lower() in senhas_comuns:

            messages.error(
                request,
                "❌ Escolha uma senha mais segura."
            )

            return redirect('criar_conta')

        # ✅ EMAIL EXISTENTE
        if User.objects.filter(
            username__iexact=email
        ).exists():

            messages.error(
                request,
                "❌ E-mail já cadastrado."
            )

            return redirect('criar_conta')

        # ✅ CRIAR USUÁRIO
        user = User.objects.create_user(

            username=email,

            email=email,

            password=senha,

            first_name=first_name,

            last_name=last_name
        )

        # ✅ SALVAR TELEFONE
        user.perfil.telefone = telefone
        user.perfil.save()

        # ✅ EMAIL BOAS-VINDAS
        try:

            from django.core.mail import send_mail

            send_mail(

                subject=(
                    "🎉 Bem-vindo à Fractions Parfums!"
                ),

                message=(
                    f"Olá, {first_name}!\n\n"
                    f"Seu cadastro foi realizado "
                    f"com sucesso.\n\n"
                    f"Obrigado por escolher "
                    f"nossa loja!"
                ),

                from_email=settings.EMAIL_HOST_USER,

                recipient_list=[email],

                fail_silently=False,
            )

        except Exception as e:

            print(
                "Erro ao enviar email:",
                e
            )

        # ✅ LOGIN AUTOMÁTICO
        login(request, user)

        request.session.save()

        messages.success(
            request,
            "✅ Conta criada e login realizado!"
        )

        # ✅ REDIRECIONA PARA CHECKOUT
        next_url = request.POST.get(
            'next'
        )

        if next_url:

            return redirect(
                next_url
            )

        return redirect('home')

    return render(
        request,
        'criar_conta.html',
        {
            'RECAPTCHA_SITE_KEY': (
                settings.RECAPTCHA_SITE_KEY
            )
        }
    )
    
    
# ✅ LOGIN
def login_usuario(request):

    if request.method == "POST":

        email = request.POST.get(
            'email',
            ''
        ).strip().lower()

        senha = request.POST.get(
            'senha'
        )

        user = authenticate(
            request,
            username=email,
            password=senha
        )

        if user is not None:

            login(request, user)

            # ✅ VINCULA CARRINHO
            vincular_carrinho_usuario(
                request,
                user
            )

            # ✅ REDIRECIONA PARA CHECKOUT
            next_url = request.POST.get(
                'next'
            )

            if next_url:

                return redirect(
                    next_url
                )

            return redirect('home')

        else:

            messages.error(
                request,
                "❌ Email ou senha inválidos."
            )

            return redirect('login')

    return render(
        request,
        'login.html'
    )

# =====================================
# ✅ MINHA CONTA
# =====================================

@login_required
def minha_conta(request):

    endereco_principal = Endereco.objects.filter(
        usuario=request.user,
        principal=True
    ).first()

    pedidos = Pedido.objects.filter(
        usuario=request.user
    ).order_by('-criado_em')

    return render(
        request,
        'usuarios/minha_conta.html',
        {
            'endereco_principal': endereco_principal,
            'pedidos': pedidos
        }
    )
    
# ✅ LOGOUT
def logout_usuario(request):
    logout(request)
    messages.success(request, "✅ Você saiu da conta.")
    return redirect('home')

# ✅ QUEM SOMOS
def quem_somos(request):
    return render(request, 'quem_somos.html')

# ✅ privacidade
def politica_privacidade(request):
    return render(request, 'politica_privacidade.html')

# ✅ TROCAS E DEVOLUÇÕES
def trocas_devolucao(request):
    return render(request, 'trocas_devolucao.html')

def perguntas_frequentes(request):
    return render(request, 'perguntas_frequentes.html')


# =====================================
# ✅ EDITAR DADOS
# =====================================
@login_required
def editar_dados(request):

    perfil = request.user.perfil

    if request.method == 'POST':

        request.user.first_name = normalizar_texto(
            request.POST.get('first_name')
        )

        request.user.last_name = normalizar_texto(
            request.POST.get('last_name')
        )

        perfil.telefone = request.POST.get(
            'telefone'
        ).strip()

        perfil.cpf = request.POST.get(
            'cpf'
        )

        request.user.save()

        perfil.save()

        messages.success(
            request,
            'Dados atualizados com sucesso!'
        )

        # ✅ VOLTA PARA CHECKOUT SE EXISTIR
        next_url = request.GET.get(
            'next'
        )

        if next_url:

            return redirect(
                next_url
            )

        return redirect('minha_conta')

    return render(
        request,
        'usuarios/editar_dados.html'
    )


# =====================================
# ✅ EDITAR ENDEREÇO
# =====================================
@login_required
def editar_endereco(request):

    endereco = Endereco.objects.filter(
        usuario=request.user,
        principal=True
    ).first()

    # ✅ cria endereço principal se não existir
    if not endereco:

        endereco = Endereco.objects.create(

            usuario=request.user,

            principal=True,

            nome_destinatario=request.user.get_full_name(),

            telefone='',

            cpf='',

            cep='',

            endereco='',

            numero='',

            complemento='',

            bairro='',

            cidade='',

            estado=''
        )

    if request.method == 'POST':

        endereco.nome_destinatario = normalizar_texto(
            request.POST.get('alias')
        )

        endereco.endereco = normalizar_texto(
            request.POST.get('endereco')
        )

        endereco.numero = request.POST.get(
            'numero',
            ''
        ).strip()

        endereco.complemento = normalizar_texto(
            request.POST.get('complemento')
        )

        endereco.bairro = normalizar_texto(
            request.POST.get('bairro')
        )

        endereco.cidade = normalizar_texto(
            request.POST.get('cidade')
        )

        endereco.estado = request.POST.get(
            'estado',
            ''
        ).strip()

        endereco.cep = re.sub(
            r'\D',
            '',
            request.POST.get('cep', '')
        )

        endereco.telefone = re.sub(
            r'\D',
            '',
            request.POST.get('telefone', '')
        )

        endereco.save()

        messages.success(
            request,
            'Endereço atualizado!'
        )

        return redirect('minha_conta')

    return render(
        request,
        'usuarios/editar_endereco.html',
        {
            'endereco': endereco
        }
    )
    
    # =====================================
# ✅ NORMALIZAR TEXTO
# =====================================

def normalizar_texto(texto):

    if not texto:
        return ''

    texto = texto.strip()

    texto = re.sub(r'\s+', ' ', texto)

    return texto.title()

