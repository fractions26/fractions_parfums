from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.carrinho.models import Carrinho

from apps.logs.models import (
    CheckoutVisitado,
    CarrinhoAbandonadoLog
)


class Command(BaseCommand):

    help = 'Gera carrinhos abandonados após 48 horas'

    def handle(self, *args, **kwargs):

        limite = timezone.now() - timedelta(hours=48)

        checkouts = CheckoutVisitado.objects.filter(
            processado=False,
            checkout_em__lte=limite
        )

        total = 0

        for checkout in checkouts:

            email = ''

            if checkout.usuario:
                email = checkout.usuario.email

            existe = CarrinhoAbandonadoLog.objects.filter(
                usuario_email=email,
                checkout_em=checkout.checkout_em
            ).exists()

            if existe:

                checkout.processado = True
                checkout.save()

                continue

            CarrinhoAbandonadoLog.objects.create(
                usuario_email=email,
                valor_total=checkout.valor_total,
                quantidade_itens=checkout.quantidade_itens,
                checkout_em=checkout.checkout_em,
                itens_removidos=True
            )

            carrinho = Carrinho.objects.filter(
                usuario=checkout.usuario
            ).first()

            if carrinho:

                carrinho.itens.all().delete()

            checkout.processado = True
            checkout.save()

            total += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'{total} carrinhos abandonados processados.'
            )
        )