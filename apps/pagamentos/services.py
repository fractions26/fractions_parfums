from django.conf import settings


def get_mp_public_key():
    return settings.MP_PUBLIC_KEY


def get_mp_access_token():
    return settings.MP_ACCESS_TOKEN