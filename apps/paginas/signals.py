from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from .models import PerfilUsuario


@receiver(post_save, sender=User)
def criar_perfil_usuario(sender, instance, created, **kwargs):

    if created:

        PerfilUsuario.objects.create(
            user=instance
        )


@receiver(post_save, sender=User)
def salvar_perfil_usuario(sender, instance, **kwargs):

    PerfilUsuario.objects.get_or_create(
        user=instance
    )