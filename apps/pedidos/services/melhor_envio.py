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