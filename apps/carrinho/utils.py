from .models import Carrinho


def get_carrinho(request):

    # ✅ Garante que exista uma sessão
    if not request.session.session_key:
        request.session.save()

    session_key = request.session.session_key

    # 🔹 Carrinho da sessão (visitante)
    carrinho_session = Carrinho.objects.filter(
        session_key=session_key
    ).first()

    # 🔥 Usuário autenticado
    if request.user.is_authenticated:

        # Obtém ou cria o carrinho do usuário
        carrinho_user, created = Carrinho.objects.get_or_create(
            usuario=request.user,
            defaults={
                "session_key": session_key
            }
        )

        # 🔥 Existe também um carrinho da sessão
        if (
            carrinho_session
            and carrinho_session != carrinho_user
        ):

            for item in carrinho_session.itens.all():

                existente = carrinho_user.itens.filter(
                    perfume=item.perfume,
                    preco_obj=item.preco_obj
                ).first()

                if existente:

                    existente.quantidade += item.quantidade
                    existente.save()

                    # Remove o item duplicado
                    item.delete()

                else:

                    # Move o item para o carrinho do usuário
                    item.carrinho = carrinho_user
                    item.save()

            # Remove o carrinho temporário
            carrinho_session.delete()

        return carrinho_user

    # ✅ Visitante
    if carrinho_session:
        return carrinho_session

    # ✅ Cria um carrinho para visitante
    return Carrinho.objects.create(
        session_key=session_key
    )