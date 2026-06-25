from django.db import models
from django.contrib.auth.models import User
from apps.produtos.models import Perfume, Preco


class Carrinho(models.Model):

    session_key = models.CharField(
        max_length=40,
        unique=True
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    def quantidade_itens(self):

        return sum(
            item.quantidade
            for item in self.itens.all()
        )

    def valor_total(self):

        return sum(
            item.preco * item.quantidade
            for item in self.itens.all()
        )

    def __str__(self):

        if self.usuario:
            return f"Carrinho de {self.usuario.email}"

        return f"Carrinho sessão {self.session_key}"


class Item(models.Model):

    carrinho = models.ForeignKey(
        Carrinho,
        related_name='itens',
        on_delete=models.CASCADE
    )

    perfume = models.ForeignKey(
        Perfume,
        on_delete=models.CASCADE
    )

    preco_obj = models.ForeignKey(
        Preco,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    tamanho = models.CharField(
        max_length=10
    )

    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantidade = models.PositiveIntegerField(
        default=1
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        unique_together = (
            'carrinho',
            'perfume',
            'preco_obj'
        )

    def subtotal(self):

        return (
            self.preco *
            self.quantidade
        )

    def __str__(self):

        return (
            f"{self.perfume.nome} - "
            f"{self.tamanho} "
            f"({self.quantidade})"
        )