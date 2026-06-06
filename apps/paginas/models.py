from django.db import models
from django.contrib.auth.models import User


class PerfilUsuario(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil'
    )

    telefone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    cpf = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    endereco = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    numero = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    bairro = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    cidade = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    cep = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Perfil - {self.user.username}"