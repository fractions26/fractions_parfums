import requests
from django.conf import settings
import uuid


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

def criar_pagamento_pix(
    valor,
    email,
    nome,
    cpf
):

    url = "https://api.mercadopago.com/v1/payments"

    headers = {
        "Authorization": f"Bearer {settings.MP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Idempotency-Key": str(uuid.uuid4())
    }

    payload = {

        "transaction_amount": float(valor),

        "description": "Pedido Fractions Parfums",

        "payment_method_id": "pix",

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

        transaction_data = (
            dados.get(
                "point_of_interaction",
                {}
            )
            .get(
                "transaction_data",
                {}
            )
        )

        dados["qr_code"] = transaction_data.get(
            "qr_code",
            ""
        )

        dados["qr_code_base64"] = transaction_data.get(
            "qr_code_base64",
            ""
        )

        dados["ticket_url"] = transaction_data.get(
            "ticket_url",
            ""
        )

        return dados

    except Exception as erro:

        return {
            "status": "error",
            "erro": str(erro),
            "http_status": 0,
            "qr_code": "",
            "qr_code_base64": "",
            "ticket_url": ""
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