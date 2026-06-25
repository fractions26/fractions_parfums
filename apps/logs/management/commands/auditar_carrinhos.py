from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.logs.models import CheckoutVisitado
from apps.pedidos.models import Pedido


class Command(BaseCommand):

    help = "Audita clientes elegíveis para recuperação de carrinho"

    def handle(self, *args, **kwargs):

        limite = timezone.now() - timedelta(hours=1)

        checkouts = CheckoutVisitado.objects.filter(
            processado=False,
            checkout_em__lte=limite
        ).select_related(
            "usuario"
        )

        self.stdout.write(
            "\n=== CLIENTES ELEGÍVEIS ===\n"
        )

        total_clientes = 0
        valor_total_geral = 0

        for checkout in checkouts:

            if not checkout.usuario:
                continue

            pedido_existe = Pedido.objects.filter(
                usuario=checkout.usuario,
                criado_em__gte=checkout.checkout_em
            ).exclude(
                status="CANCELADO"
            ).exists()

            if pedido_existe:
                continue

            total_clientes += 1

            valor_total_geral += float(
                checkout.valor_total
            )

            self.stdout.write(
                f"Cliente: {checkout.usuario.email}"
            )

            self.stdout.write(
                f"Itens: {checkout.quantidade_itens}"
            )

            self.stdout.write(
                f"Valor: R$ {checkout.valor_total}"
            )

            self.stdout.write(
                f"Checkout Em: {checkout.checkout_em}"
            )

            self.stdout.write(
                f"Email 1H: {'SIM' if checkout.email_1_enviado else 'NÃO'}"
            )

            self.stdout.write(
                f"Email 24H: {'SIM' if checkout.email_2_enviado else 'NÃO'}"
            )

            self.stdout.write(
                f"Email 72H: {'SIM' if checkout.email_3_enviado else 'NÃO'}"
            )

            self.stdout.write(
                "-" * 60
            )

        self.stdout.write("\n=== RESUMO ===\n")

        self.stdout.write(
            f"Clientes elegíveis: {total_clientes}"
        )

        self.stdout.write(
            f"Valor total recuperável: R$ {valor_total_geral:,.2f}"
        )

        self.stdout.write(
            "\n========================\n"
        )