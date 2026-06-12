from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

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

    cpf_validator = RegexValidator(
        regex=r'^\d{11}$',
        message='CPF deve conter 11 números'
    )

    cpf = models.CharField(
        max_length=11,
        validators=[cpf_validator],
        blank=True,
        null=True
    )


    # ✅ IDENTIFICAÇÃO ENDEREÇO
    alias = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # ✅ ENDEREÇO
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

    complemento = models.CharField(
        max_length=255,
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

    pais = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='Brasil'
    )

    def __str__(self):
        return f"Perfil - {self.user.username}"