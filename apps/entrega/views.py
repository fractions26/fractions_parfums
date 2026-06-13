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

    # ✅ validação básica
    if not cep or len(cep) < 8:
        return JsonResponse({
            "success": False,
            "erro": "CEP inválido"
        })

    url = "https://sandbox.melhorenvio.com.br/api/v2/me/shipment/calculate"

    headers = {
        "Authorization": f"Bearer {settings.MELHOR_ENVIO_TOKEN}", # 🔥 coloca seu token
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "from": {"postal_code": "82590100"},  # ✅ origem real (sua loja)
        "to": {"postal_code": cep},          # ✅ destino (cliente)

        "products": [
            {
                "id": "1",
                "width": 10,      # largura
                "height": 4,      # altura
                "length": 10,     # comprimento
                "weight": 0.2,    # ✅ 200g ideal para decant
                "quantity": 1
            }
        ]
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            verify=False  # 🔥 CORREÇÃO DO SSL
        )

        data = response.json()

        return JsonResponse(data, safe=False)

    except Exception as e:
        return JsonResponse({
            "success": False,
            "erro": str(e)
        })