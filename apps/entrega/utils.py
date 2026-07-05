from decimal import Decimal

NORTE_NORDESTE = [
    "50","51","52","53","54","55","56","57","58","59",
    "60","61","62","63","64","65","66","67","68","69"
]


def possui_frete_gratis(subtotal, cep):

    prefixo = str(cep or "")[:2]

    limite = Decimal("199")

    if prefixo in NORTE_NORDESTE:
        limite = Decimal("300")

    return Decimal(subtotal) >= limite