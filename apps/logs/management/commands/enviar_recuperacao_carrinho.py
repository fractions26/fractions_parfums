from datetime import timedelta

from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from apps.carrinho.models import Carrinho

from apps.logs.models import (
    CheckoutVisitado,
    CarrinhoAbandonadoLog
)


class Command(BaseCommand):

    help = "Envia emails de recuperação de carrinho"

    def handle(self, *args, **kwargs):

        agora = timezone.now()

        self.enviar_email_1h(agora)
        self.enviar_email_24h(agora)
        self.enviar_email_72h(agora)

    def enviar_email(self, checkout, assunto):
        
        if not checkout.usuario:
            return False

        carrinho = Carrinho.objects.filter(
            usuario=checkout.usuario
        ).first()

        if not carrinho:
            return False

        itens = carrinho.itens.select_related(
            "perfume"
        )

        if not itens.exists():
            return False

        total = sum(
            item.preco * item.quantidade
            for item in itens
        )

        from django.conf import settings

        print("EMAIL_HOST =", settings.EMAIL_HOST)
        print("EMAIL_USER =", settings.EMAIL_HOST_USER)
        print(
            "EMAIL_PASSWORD =",
            bool(settings.EMAIL_HOST_PASSWORD)
        )
        print("EMAIL_PORT =", settings.EMAIL_PORT)

        try:

            html = render_to_string(
                "emails/carrinho_abandonado.html",
                {
                    "nome": (
                        checkout.usuario.first_name
                        or checkout.usuario.email
                    ),
                    "itens": itens,
                    "total": total,
                }
            )

            email = EmailMultiAlternatives(

                subject=assunto,

                body="Carrinho abandonado",

                from_email=(
                    "Fractions Parfums "
                    "<contato@fractionsparfums.com.br>"
                ),

                to=[checkout.usuario.email]
            )

            email.attach_alternative(
                html,
                "text/html"
            )

            email.send()

            return True

        except Exception as erro:

            self.stdout.write(
                self.style.ERROR(
                    f"Erro ao enviar email: {erro}"
                )
            )

            return False

    def enviar_email_1h(self, agora):

        limite = agora - timedelta(hours=1)

        checkouts = CheckoutVisitado.objects.filter(
            processado=False,
            email_1_enviado=False,
            checkout_em__lte=limite
        )

        for checkout in checkouts:

            enviado = self.enviar_email(
                checkout,
                "🖤 Você esqueceu seus perfumes no carrinho"
            )

            if enviado:

                checkout.email_1_enviado = True
                checkout.email_1_enviado_em = agora

                checkout.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[1H] {checkout.usuario.email}"
                    )
                )

    def enviar_email_24h(self, agora):

        limite = agora - timedelta(hours=24)

        checkouts = CheckoutVisitado.objects.filter(
            processado=False,
            email_2_enviado=False,
            checkout_em__lte=limite
        )

        for checkout in checkouts:

            enviado = self.enviar_email(
                checkout,
                "🖤 Seus perfumes ainda estão te esperando"
            )

            if enviado:

                checkout.email_2_enviado = True
                checkout.email_2_enviado_em = agora

                checkout.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[24H] {checkout.usuario.email}"
                    )
                )

    def enviar_email_72h(self, agora):

        limite = agora - timedelta(hours=72)

        checkouts = CheckoutVisitado.objects.filter(
            processado=False,
            email_3_enviado=False,
            checkout_em__lte=limite
        )

        for checkout in checkouts:

            enviado = self.enviar_email(
                checkout,
                "⏳ Última oportunidade para finalizar sua compra"
            )

            if enviado:

                checkout.email_3_enviado = True
                checkout.email_3_enviado_em = agora

                checkout.processado = True

                checkout.save()

                CarrinhoAbandonadoLog.objects.get_or_create(
                    usuario_email=checkout.usuario.email,
                    checkout_em=checkout.checkout_em,
                    defaults={
                        "valor_total": checkout.valor_total,
                        "quantidade_itens": checkout.quantidade_itens,
                        "itens_removidos": False
                    }
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[72H] {checkout.usuario.email}"
                    )
                )