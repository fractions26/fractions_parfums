import requests

from django.conf import settings


# =====================================
# ✅ EMBALAGEM PADRÃO FRACTIONS
# =====================================

LARGURA = 11
ALTURA = 5
COMPRIMENTO = 16
PESO = 0.4


# =====================================
# ✅ HEADERS MELHOR ENVIO
# =====================================

def headers():

    return {
        "Authorization": (
            f"Bearer {settings.MELHOR_ENVIO_TOKEN}"
        ),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": (
            "Fractions Parfums "
            "(contato@fractionsparfums.com.br)"
        )
    }


# =====================================
# ✅ MAPEIA TRANSPORTADORA
# =====================================

def obter_transportadora(pedido):

    nome = (
        pedido.frete_nome or ""
    ).upper()

    if "SEDEX" in nome:
        return "Correios"

    if "JADLOG" in nome:
        return "Jadlog"

    if "LOGGI" in nome:
        return "Loggi"

    if "JET" in nome:
        return "JeT"

    if "J&T" in nome:
        return "JeT"

    return nome


# =====================================
# ✅ DADOS DO DESTINATÁRIO
# =====================================

def dados_destinatario(pedido):

    return {
        "nome": pedido.nome,
        "email": pedido.email,
        "telefone": pedido.telefone,
        "cpf": pedido.cpf,
        "cep": pedido.cep,
        "endereco": pedido.endereco,
        "numero": pedido.numero,
        "complemento": pedido.complemento,
        "cidade": pedido.cidade,
        "estado": pedido.estado,
    }


# =====================================
# ✅ DADOS DA EMBALAGEM
# =====================================

def dados_embalagem():

    return {
        "width": LARGURA,
        "height": ALTURA,
        "length": COMPRIMENTO,
        "weight": PESO,
    }


# =====================================
# ✅ DADOS COMPLETOS DO ENVIO
# =====================================

def dados_envio(pedido):

    return {
        "nome": pedido.nome,
        "email": pedido.email,
        "cpf": pedido.cpf,
        "telefone": pedido.telefone,
        "cep": pedido.cep,
        "endereco": pedido.endereco,
        "numero": pedido.numero,
        "complemento": pedido.complemento,
        "cidade": pedido.cidade,
        "estado": pedido.estado,
        "frete": pedido.frete_nome,
        "transportadora": obter_transportadora(
            pedido
        ),
        "peso": PESO,
        "largura": LARGURA,
        "altura": ALTURA,
        "comprimento": COMPRIMENTO,
    }

# =====================================
# ✅ TESTE CRIAÇÃO DE ENVIO
# =====================================

def criar_payload_envio(pedido):

    dados = dados_envio(pedido)

    return {
        "pedido": pedido.codigo,
        "destinatario": {
            "nome": dados["nome"],
            "email": dados["email"],
            "cpf": dados["cpf"],
            "telefone": dados["telefone"],
            "cep": dados["cep"],
            "endereco": dados["endereco"],
            "numero": dados["numero"],
            "complemento": dados["complemento"],
            "cidade": dados["cidade"],
            "estado": dados["estado"],
        },
        "volumes": [
            {
                "peso": dados["peso"],
                "largura": dados["largura"],
                "altura": dados["altura"],
                "comprimento": dados["comprimento"],
            }
        ]
    }

# =====================================
# ✅ TESTE CONEXÃO MELHOR ENVIO
# =====================================

def consultar_usuario():

    response = requests.get(
        "https://melhorenvio.com.br/api/v2/me",
        headers=headers(),
        timeout=30
    )

    return {
        "status_code": response.status_code,
        "body": response.json()
    }
    

# =====================================
# ✅ OBTÉM SERVIÇO MELHOR ENVIO
# =====================================

def listar_servicos():

    response = requests.get(
        "https://melhorenvio.com.br/api/v2/me/shipment/services",
        headers=headers(),
        timeout=30
    )

    response.raise_for_status()

    return response.json()

# =====================================
# ✅ OBTÉM ID DO SERVIÇO
# =====================================

def obter_servico_pedido(pedido):

    frete = (
        pedido.frete_nome or ""
    ).upper()

    servicos = listar_servicos()

    for servico in servicos:

        nome_servico = (
            servico.get("name", "")
            .upper()
        )

        empresa = (
            servico.get("company", {})
            .get("name", "")
            .upper()
        )

        texto = (
            f"{empresa} {nome_servico}"
        )

        if "SEDEX" in frete and "SEDEX" in texto:
            return servico

        if "LOGGI" in frete and "LOGGI" in texto:
            return servico

        if "JADLOG" in frete and "JADLOG" in texto:
            return servico

        if (
            "JET" in frete
            and "JET" in texto
        ):
            return servico

    return None


# =====================================
# ✅ DADOS RESUMIDOS DO SERVIÇO
# =====================================

def obter_servico_id(pedido):

    servico = obter_servico_pedido(
        pedido
    )

    if not servico:
        return None

    return servico["id"]


# =====================================
# ✅ DADOS DO SERVIÇO SELECIONADO
# =====================================

def resumo_servico(pedido):

    servico = obter_servico_pedido(
        pedido
    )

    if not servico:

        return None

    return {
        "service_id": servico["id"],
        "service_name": servico["name"],
        "company_name": servico["company"]["name"],
    }

# =====================================
# ✅ MONTA DADOS PARA ENVIO
# =====================================

def preparar_envio(pedido):

    return {
        "pedido": pedido.codigo,
        "servico": resumo_servico(
            pedido
        ),
        "destinatario": dados_destinatario(
            pedido
        ),
        "embalagem": dados_embalagem(),
    }
    
    
# =====================================
# ✅ CRIAR ENVIO (PREPARAÇÃO)
# =====================================

def criar_envio_dados(pedido):

    dados = preparar_envio(
        pedido
    )

    return {
        "pedido": dados["pedido"],
        "service_id": (
            dados["servico"]["service_id"]
        ),
        "transportadora": (
            dados["servico"]["company_name"]
        ),
        "destinatario": (
            dados["destinatario"]
        ),
        "embalagem": (
            dados["embalagem"]
        ),
    }
    
# =====================================
# ✅ PRIMEIRO TESTE DE ENVIO
# =====================================

def testar_integracao_envio(pedido):

    dados = criar_envio_dados(
        pedido
    )

    return {
        "pedido": dados["pedido"],
        "service_id": dados["service_id"],
        "transportadora": dados["transportadora"],
        "cep": dados["destinatario"]["cep"],
        "destinatario": dados["destinatario"]["nome"],
    }
    
# =====================================
# ✅ PAYLOAD CARRINHO MELHOR ENVIO
# =====================================

def payload_carrinho(pedido):
    
    dados = criar_envio_dados(
        pedido
    )

    return {

        "service": dados["service_id"],

        "from": dados_remetente(),

        "to": {
            "name": dados["destinatario"]["nome"],
            "email": dados["destinatario"]["email"],
            "phone": dados["destinatario"]["telefone"],
            "document": dados["destinatario"]["cpf"],
            "address": dados["destinatario"]["endereco"],
            "number": dados["destinatario"]["numero"],
            "complement": dados["destinatario"]["complemento"],
            "district": "Centro",
            "city": dados["destinatario"]["cidade"],
            "country_id": "BR",
            "state_abbr": dados["destinatario"]["estado"],
            "postal_code": dados["destinatario"]["cep"],
        },

        "products": [
            {
                "name": f"Pedido {pedido.codigo}",
                "quantity": "1",
                "unitary_value": str(
                    pedido.total
                )
            }
        ],

        "volumes": [
            {
                "width": dados["embalagem"]["width"],
                "height": dados["embalagem"]["height"],
                "length": dados["embalagem"]["length"],
                "weight": dados["embalagem"]["weight"],
            }
        ],

        "options": {
            "platform": "Fractions Parfums",
            "insurance_value": float(
                pedido.total
            ),
            "receipt": False,
            "own_hand": False,
            "reverse": False,
            "non_commercial": True,
        }
    }
    
# =====================================
# ✅ REMETENTE FRACTIONS
# =====================================

def dados_remetente():

    return {
        "name": "Douglas Antonio",
        "email": "www.dls14@gmail.com",
        "phone": "41991970399",
        "document": "06533837974",
        "address": "Rodovia Br 116",
        "complement": "Bloco 2 ap 507",
        "number": "2785",
        "district": "Atuba",
        "city": "Curitiba",
        "country_id": "BR",
        "postal_code": "82590100",
        "state_abbr": "PR",
    }
    
# =====================================
# ✅ INSERIR FRETE NO CARRINHO
# =====================================

def inserir_frete_carrinho(pedido):

    payload = payload_carrinho(
        pedido
    )

    response = requests.post(
        "https://melhorenvio.com.br/api/v2/me/cart",
        headers=headers(),
        json=payload,
        timeout=60
    )

    try:
        body = response.json()
    except Exception:
        body = response.text

    return {
        "status_code": response.status_code,
        "body": body,
    }

# =====================================
# ✅ COMPRAR ETIQUETA
# =====================================

def comprar_etiqueta(pedido):

    response = requests.post(

        "https://melhorenvio.com.br/api/v2/me/shipment/checkout",

        headers=headers(),

        json={
            "orders": [
                pedido.melhor_envio_id
            ]
        },

        timeout=60
    )

    try:
        body = response.json()

    except Exception:

        body = response.text

    return {
        "status_code": response.status_code,
        "body": body,
    }
    
# =====================================
# ✅ CONSULTAR ENVIO
# =====================================

def consultar_envio(pedido):

    response = requests.get(
        (
            "https://melhorenvio.com.br/api/v2/me/shipment/"
            f"{pedido.melhor_envio_id}"
        ),
        headers=headers(),
        timeout=60
    )

    try:
        body = response.json()

    except Exception:

        body = response.text

    return {
        "status_code": response.status_code,
        "body": body,
    }