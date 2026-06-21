from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out
)
from django.dispatch import receiver

from .models import LoginLog


@receiver(user_logged_in)
def registrar_login(sender, request, user, **kwargs):

    LoginLog.objects.create(
        email=user.email or user.username,
        evento='LOGIN',
        sucesso=True,
        ip=request.META.get('REMOTE_ADDR', ''),
        user_agent=request.META.get(
            'HTTP_USER_AGENT',
            ''
        )
    )


@receiver(user_logged_out)
def registrar_logout(sender, request, user, **kwargs):

    if user:

        LoginLog.objects.create(
            email=user.email or user.username,
            evento='LOGOUT',
            sucesso=True,
            ip=request.META.get('REMOTE_ADDR', ''),
            user_agent=request.META.get(
                'HTTP_USER_AGENT',
                ''
            )
        )