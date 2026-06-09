import uuid


def gerar_codigo_pedido():

    return str(uuid.uuid4())[:8].upper()