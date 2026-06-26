from django.db import models
from django.contrib.auth.models import User


class Cupom(models.Model):

    codigo = models.CharField(
        max_length=50,
        unique=True
    )

    descricao = models.CharField(
        max_length=200,
        blank=True
    )

    desconto_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    ativo = models.BooleanField(
        default=True
    )

    primeira_compra = models.BooleanField(
        default=False
    )

    data_inicio = models.DateTimeField(
        null=True,
        blank=True
    )

    data_fim = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.codigo
