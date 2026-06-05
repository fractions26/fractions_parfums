from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Carrinho, Item


@receiver(user_logged_in)
def merge_carrinho(sender, request, user, **kwargs):

    print("🔥 SIGNAL DISPARADO")
    print("👤 USER:", user)

    # ✅ CORREÇÃO CRÍTICA
    if not request.session.session_key:
        request.session.save()

    print("🧩 SESSION KEY (nova):", request.session.session_key)

    # ✅ NÃO confiar só na session_key
    carrinho_session = Carrinho.objects.filter(
        usuario__isnull=True
    ).order_by('-id').first()

    print("📦 CARRINHO SESSION ENCONTRADO:", carrinho_session)

    if not carrinho_session:
        print("❌ Nenhum carrinho de sessão encontrado")
        return

    # ✅ pega ou cria carrinho do usuário
    carrinho_usuario, created = Carrinho.objects.get_or_create(
        usuario=user,
        defaults={"session_key": request.session.session_key}
    )

    print("🧑‍💼 CARRINHO DO USUÁRIO:", carrinho_usuario)

    for item in carrinho_session.itens.all():

        existente = Item.objects.filter(
            carrinho=carrinho_usuario,
            perfume=item.perfume,
            preco_obj=item.preco_obj
        ).first()

        if existente:
            existente.quantidade += item.quantidade
            existente.save()
            print(f"➕ Item somado: {item}")
        else:
            item.carrinho = carrinho_usuario
            item.save()
            print(f"➡️ Item movido: {item}")

    carrinho_session.delete()

    print("✅ MERGE FINALIZADO COM SUCESSO")