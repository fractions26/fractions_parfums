import requests
from django.conf import settings


def get_mp_public_key():
    return settings.MP_PUBLIC_KEY


def criar_pagamento_cartao(
    token,
    valor,
    email,
    nome,
    cpf,
    payment_method_id="visa"
):

    url = "https://api.mercadopago.com/v1/payments"

    headers = {
        "Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Idempotency-Key": token
    }

    payload = {
        "transaction_amount": float(valor),

        "token": token,

        "description": "Pedido Fractions Parfums",

        "installments": 1,

        "payment_method_id": payment_method_id,

        "payer": {
            "email": email,
            "first_name": nome,
            "identification": {
                "type": "CPF",
                "number": cpf
            }
        }
    }

    try:

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        dados = response.json()

        dados["http_status"] = response.status_code

        dados["bandeira_cartao"] = dados.get(
            "payment_method_id",
            ""
        )

        return dados

    except Exception as erro:

        return {
            "status": "error",
            "erro": str(erro),
            "http_status": 0
        }


def testar_credenciais():

    url = "https://api.mercadopago.com/users/me"

    headers = {
        "Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    return response.json()