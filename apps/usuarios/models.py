from django.db import models
from django.contrib.auth.models import User


class Endereco(models.Model):

    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='enderecos'
    )

    nome_destinatario = models.CharField(
        max_length=255
    )

    telefone = models.CharField(
        max_length=20
    )

    cpf = models.CharField(
        max_length=14
    )

    cep = models.CharField(
        max_length=10
    )

    endereco = models.CharField(
        max_length=255
    )

    numero = models.CharField(
        max_length=20
    )

    complemento = models.CharField(
        max_length=255,
        blank=True
    )

    bairro = models.CharField(
        max_length=255
    )

    cidade = models.CharField(
        max_length=100
    )

    estado = models.CharField(
        max_length=2
    )

    principal = models.BooleanField(
        default=False
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

    def __str__(self):

        return (
            f'{self.endereco}, '
            f'{self.numero} - '
            f'{self.cidade}'
        )