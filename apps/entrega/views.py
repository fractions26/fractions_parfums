from django.shortcuts import render
from django.http import JsonResponse
import requests
import urllib3
from django.conf import settings

# ✅ remove aviso SSL (apenas ambiente local)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# =========================
# ✅ CHECKOUT
# =========================
def checkout(request):
    return render(request, 'pedidos/checkout.html')


# =========================
# ✅ CALCULAR FRETE (MELHOR ENVIO)
# =========================
def calcular_frete(request):
    
    cep = request.GET.get("cep")

    if not cep or len(cep) < 8:
        return JsonResponse({
            "success": False,
            "fretes": [],
            "erro": "CEP inválido"
        })

    url = "https://sandbox.melhorenvio.com.br/api/v2/me/shipment/calculate"

    headers = {
        "Authorization": f"Bearer {settings.MELHOR_ENVIO_TOKEN}",
        "Accept": "application/json",
        "Content-Type": "application/json"
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
                "height": 2,
                "length": 11,
                "weight": 0.3,
                "quantity": 1
            }
        ]
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            verify=False
        )
        
        print("STATUS:", response.status_code)
        print("BODY:", response.text)


        data = response.json()

        return JsonResponse({
            "success": True,
            "fretes": data
        })

    except Exception as e:
        return JsonResponse({
            "success": False,
            "fretes": [],
            "erro": str(e)
        })