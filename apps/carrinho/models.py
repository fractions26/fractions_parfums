from django.db import models
from django.contrib.auth.models import User
from apps.produtos.models import Perfume, Preco


class Carrinho(models.Model):
    session_key = models.CharField(max_length=40, unique=True)

    # ✅ NOVO CAMPO (ESSENCIAL)
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        if self.usuario:
            return f"Carrinho de {self.usuario}"
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

    tamanho = models.CharField(max_length=10)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('carrinho', 'perfume', 'preco_obj')

    def __str__(self):
        return f"{self.perfume.nome} - {self.tamanho} ({self.quantidade})"