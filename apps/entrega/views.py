from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.conf import settings


# =========================
# ✅ CHECKOUT
# =========================
def checkout(request):
    return render(request, 'pedidos/checkout.html')


# =========================
# ✅ CALCULAR FRETE (MELHOR ENVIO + CONTINGÊNCIA)
# =========================
def calcular_frete(request):

    cep = request.GET.get("cep", "")

    if not cep or len(cep) < 8:

        return JsonResponse({
            "success": False,
            "fretes": [],
            "erro": "CEP inválido"
        })

    url = "https://melhorenvio.com.br/api/v2/me/shipment/calculate"

    headers = {
        "Authorization": f"Bearer {settings.MELHOR_ENVIO_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": (
            "Fractions Parfums "
            "(contato@fractionsparfums.com.br)"
        )
    }

    payload = {
        "from": {
            "postal_code": "82590100"
        },
        "to": {
            "postal_code": cep
        },
        "products": [
            {
                "id": "1",
                "width": 16,
                "height": 5,
                "length": 11,
                "weight": 0.4,
                "quantity": 1
            }
        ]
    }

    try:

        print(
            "TOKEN TAMANHO:",
            len(settings.MELHOR_ENVIO_TOKEN or "")
        )

        print(
            "TOKEN INICIO:",
            (settings.MELHOR_ENVIO_TOKEN or "")[:50]
        )

        print(
            "TOKEN FINAL:",
            (settings.MELHOR_ENVIO_TOKEN or "")[-100:]
        )

        # ✅ TESTA O TOKEN
        teste = requests.get(
            "https://melhorenvio.com.br/api/v2/me",
            headers=headers,
            timeout=15
        )

        print(
            "ME STATUS:",
            teste.status_code
        )

        print(
            "ME BODY:",
            teste.text
        )

        # ✅ CONSULTA FRETE
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=15
        )

        print(
            "STATUS:",
            response.status_code
        )

        print(
            "BODY:",
            response.text
        )

        data = response.json()

        if (
            response.status_code == 200 and
            isinstance(data, list)
        ):

            fretes_validos = [
                frete
                for frete in data
                if not frete.get("error")
            ]

            if fretes_validos:

                return JsonResponse({
                    "success": True,
                    "fretes": fretes_validos
                })

        raise Exception(
            f"Melhor Envio retornou {response.status_code}"
        )

    except Exception as e:

        print(
            "⚠️ CONTINGÊNCIA DE FRETE:",
            str(e)
        )

        prefixo = str(cep)[:2]

        sul_sudeste = [
            "01","02","03","04","05","06","07","08","09",
            "10","11","12","13","14","15","16","17","18","19",
            "20","21","22","23","24","25","26","27","28",
            "29","30","31","32","33","34","35","36","37","38","39",
            "80","81","82","83","84","85","86","87","88","89"
        ]

        if prefixo in sul_sudeste:

            valor = "14.90"
            prazo = 5

        else:

            valor = "40.90"
            prazo = 10

        return JsonResponse({
            "success": True,
            "contingencia": True,
            "fretes": [
                {
                    "id": "contingencia",
                    "name": "Frete Econômico",
                    "price": valor,
                    "delivery_time": prazo,
                    "company": {
                        "name": "Fractions Parfums",
                        "picture": ""
                    }
                }
            ]
        })
        
def gerar_token_melhor_envio(request):
    
    code = request.GET.get("code")

    response = requests.post(
        "https://www.melhorenvio.com.br/oauth/token",
        headers={
            "Accept": "application/json",
            "User-Agent": (
                "Fractions Parfums "
                "(contato@fractionsparfums.com.br)"
            )
        },
        data={
            "grant_type": "authorization_code",
            "client_id": 26576,
            "client_secret": settings.MELHOR_ENVIO_CLIENT_SECRET,
            "redirect_uri": "https://www.fractionsparfums.com.br",
            "code": code
        }
    )

    print("TOKEN STATUS:", response.status_code)
    print("TOKEN BODY:", response.text)

    return JsonResponse({
        "status": response.status_code,
        "body": response.text
    })