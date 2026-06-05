from django.shortcuts import render
from django.http import JsonResponse
import requests
import urllib3

# ✅ remove aviso SSL (apenas ambiente local)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# =========================
# ✅ CHECKOUT
# =========================
def checkout(request):
    return render(request, 'checkout.html')


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
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5NTYiLCJqdGkiOiJiMzNhMWVhZGJkMzg3ZGU5MmNlNGI4YjcwZDBiNWExZWE5ODY5YzQxNzQ0ZDliNjY5ZDY3NTdlZGZiMTU1ZjhjOTZkMTRmMDUwY2QwMDkyYSIsImlhdCI6MTc4MDU4NDA3Ni4zODIwNTEsIm5iZiI6MTc4MDU4NDA3Ni4zODIwNTQsImV4cCI6MTgxMjEyMDA3Ni4zNzI4MTMsInN1YiI6ImExZjE3MzUxLTQ5NWQtNDRhMC05NmZiLTEyMGU5MTJlMzU5MyIsInNjb3BlcyI6WyJjYXJ0LXJlYWQiLCJjYXJ0LXdyaXRlIiwiY29tcGFuaWVzLXJlYWQiLCJjb21wYW5pZXMtd3JpdGUiLCJjb3Vwb25zLXJlYWQiLCJjb3Vwb25zLXdyaXRlIiwibm90aWZpY2F0aW9ucy1yZWFkIiwib3JkZXJzLXJlYWQiLCJwcm9kdWN0cy1yZWFkIiwicHJvZHVjdHMtZGVzdHJveSIsInByb2R1Y3RzLXdyaXRlIiwicHVyY2hhc2VzLXJlYWQiLCJzaGlwcGluZy1jYWxjdWxhdGUiLCJzaGlwcGluZy1jYW5jZWwiLCJzaGlwcGluZy1jaGVja291dCIsInNoaXBwaW5nLWNvbXBhbmllcyIsInNoaXBwaW5nLWdlbmVyYXRlIiwic2hpcHBpbmctcHJldmlldyIsInNoaXBwaW5nLXByaW50Iiwic2hpcHBpbmctc2hhcmUiLCJzaGlwcGluZy10cmFja2luZyIsImVjb21tZXJjZS1zaGlwcGluZyIsInRyYW5zYWN0aW9ucy1yZWFkIiwidXNlcnMtcmVhZCIsInVzZXJzLXdyaXRlIiwid2ViaG9va3MtcmVhZCIsIndlYmhvb2tzLXdyaXRlIiwid2ViaG9va3MtZGVsZXRlIiwidGRlYWxlci13ZWJob29rIl19.rDkd2RgPdlsNCHs-D_gw_d2PR0-lX0EWGAcCsDMLLwkqfxu8vdxTBkyzkQ7ZhfoUQ5q6Z1l_pkz-T5xZRu0JVTD9nedUntCTNz8dkixj79qeDmRxwrk3cQ030vz-5VESWRmpDUBcGI28gVZi07mr2hdmiDZym9WO4OITGiZRze7BQBUugjLOJBXu1jacrJTQLjRHOWc8b4g-DnUPDs8f_RiiCFCgDtYsywfU4AST5hIo-3SyTmzMXvJwt6w2UUEMxCYsZ5yWUF9Fbfz9c2zP5vl6tm7hGa_Htp9IdBpX55LnjlmTexcs8qROU_zx107nyz4RxvEvXHzUf8Fk-QfI1aAWap3edaKPAjmVaFDPNc9B33bkZy1I9of5jTejcwCcuA6rXVBxnshDYZsQ-cf_z4Of9XMfrBIdvf9v4LsThutkg2DBWkjviNXwXuQCusUycReArgkNGIZDNbPBcmiwrCg3X3Gze-XXh8T1MkSvd5J5icogPf4lMb8UAjTQ0JP7g77TtjLss_V55boGYL8zjfJbCyzoHnJbUBGWFxAT9txhS0BvZXK9DRasdVac29sxPxr24k-S8pnAcEPckZDx9WUffP_lZv9-qL-parDhtp7R5cMTiKI-qJ8t_HFMJhH_XWqu1BQ5ZBj2FCwDxBnyxOquw3FWa21KvGWcgE4H3yI",  # 🔥 coloca seu token
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