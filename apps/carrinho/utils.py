from .models import Carrinho

def get_carrinho(request):

    # ✅ garante session ativa
    if not request.session.session_key:
        request.session.save()

    session_key = request.session.session_key

    # 🔹 carrinho da sessão (visitante)
    carrinho_session = Carrinho.objects.filter(
        session_key=session_key
    ).first()

    # 🔥 se estiver logado
    if request.user.is_authenticated:

        carrinho_user = Carrinho.objects.filter(
            usuario=request.user
        ).first()

        # ✅ se já existe carrinho do usuário
        if carrinho_user:

            # 🔥 MIGRA itens da session se existir
            if carrinho_session and carrinho_session != carrinho_user:
                for item in carrinho_session.itens.all():
                    item.carrinho = carrinho_user
                    item.save()

                carrinho_session.delete()

            return carrinho_user

        # ✅ se NÃO existe carrinho do usuário → usa o da sessão
        if carrinho_session:
            carrinho_session.usuario = request.user
            carrinho_session.save()
            return carrinho_session

        # ✅ fallback
        return Carrinho.objects.create(
            usuario=request.user,
            session_key=session_key
        )

    # ✅ visitante (não logado)
    if carrinho_session:
        return carrinho_session

    return Carrinho.objects.create(session_key=session_key)