from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from .models import Carrinho, Item


@receiver(user_logged_in)
def merge_carrinho(sender, request, user, **kwargs):

    print("=" * 60)
    print("🔥 SIGNAL DISPARADO")
    print(f"👤 USER: {user}")

    if not request.session.session_key:
        request.session.save()

    print(f"🧩 SESSION KEY: {request.session.session_key}")

    # Procura somente carrinho sem usuário que possua itens.
    carrinho_session = (
        Carrinho.objects
        .filter(usuario__isnull=True)
        .exclude(itens__isnull=True)
        .distinct()
        .order_by("-criado_em")
        .first()
    )

    print("📦 CARRINHO SESSION:", carrinho_session)

    if not carrinho_session:
        print("❌ Nenhum carrinho anônimo encontrado")
        print("=" * 60)
        return

    # Obtém ou cria o carrinho do usuário
    carrinho_usuario, created = Carrinho.objects.get_or_create(
        usuario=user,
        defaults={
            "session_key": request.session.session_key
        }
    )

    print("🛒 CARRINHO USUÁRIO:", carrinho_usuario)

    for item in carrinho_session.itens.all():

        existente = Item.objects.filter(
            carrinho=carrinho_usuario,
            perfume=item.perfume,
            preco_obj=item.preco_obj
        ).first()

        if existente:

            existente.quantidade += item.quantidade
            existente.save()

            item.delete()

            print(f"➕ Somado: {existente}")

        else:

            item.carrinho = carrinho_usuario
            item.save()

            print(f"➡️ Movido: {item}")

    # Remove o carrinho anônimo somente se ficou vazio
    if not carrinho_session.itens.exists():
        carrinho_session.delete()
        print("🗑️ Carrinho anônimo removido")

    print("✅ MERGE FINALIZADO")
    print("=" * 60)