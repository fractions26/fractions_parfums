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

    # 🔥 usuário autenticado
    if request.user.is_authenticated:

        carrinho_user = Carrinho.objects.filter(
            usuario=request.user
        ).first()

        # ✅ usuário já possui carrinho
        if carrinho_user:

            # 🔥 existe também um carrinho da sessão
            if carrinho_session and carrinho_session != carrinho_user:

                for item in carrinho_session.itens.all():

                    existente = carrinho_user.itens.filter(
                        perfume=item.perfume,
                        preco_obj=item.preco_obj
                    ).first()

                    if existente:
                        existente.quantidade += item.quantidade
                        existente.save()

                        # remove o item duplicado do carrinho da sessão
                        item.delete()

                    else:
                        item.carrinho = carrinho_user
                        item.save()

                # mantém a sessão atual vinculada ao carrinho do usuário
                carrinho_user.session_key = session_key
                carrinho_user.save(update_fields=["session_key"])

                # remove o carrinho temporário
                carrinho_session.delete()

            return carrinho_user

        # ✅ usuário não tinha carrinho
        if carrinho_session:
            carrinho_session.usuario = request.user
            carrinho_session.session_key = session_key
            carrinho_session.save()

            return carrinho_session

        # ✅ cria um novo carrinho
        return Carrinho.objects.create(
            usuario=request.user,
            session_key=session_key
        )

    # ✅ visitante
    if carrinho_session:
        return carrinho_session

    # ✅ cria carrinho para visitante
    return Carrinho.objects.create(
        session_key=session_key
    )