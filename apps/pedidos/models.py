from django.db import models
from django.contrib.auth.models import User


STATUS_CHOICES = [
    ('PENDENTE', 'Pendente'),
    ('AGUARDANDO_PAGAMENTO', 'Aguardando Pagamento'),
    ('PAGO', 'Pago'),
    ('ENVIADO', 'Enviado'),
    ('FINALIZADO', 'Finalizado'),
    ('CANCELADO', 'Cancelado'),
    ('REEMBOLSADO', 'Reembolsado'),
]

class Pedido(models.Model):
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    codigo = models.CharField(
        max_length=20,
        unique=True
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    frete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    frete_nome = models.CharField(
        max_length=255,
        blank=True
    )

    frete_prazo = models.CharField(
        max_length=100,
        blank=True
    )

    # =====================================
    # ✅ MELHOR ENVIO
    # =====================================

    melhor_envio_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    codigo_rastreio = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    transportadora = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    url_etiqueta = models.URLField(
        blank=True,
        null=True
    )

    status_envio = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    etiqueta_gerada = models.BooleanField(
        default=False
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # ✅ CUPOM
    cupom_codigo = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    desconto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='PENDENTE'
    )

    estoque_baixado = models.BooleanField(
        default=False
    )

    # =====================================
    # ✅ MERCADO PAGO
    # =====================================

    metodo_pagamento = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    mercadopago_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    mercadopago_status = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    bandeira_cartao = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    parcelas = models.PositiveIntegerField(
        default=1
    )

    nome = models.CharField(
        max_length=255
    )

    email = models.EmailField()

    telefone = models.CharField(
        max_length=20,
        blank=True
    )

    cpf = models.CharField(
        max_length=14,
        blank=True,
        null=True
    )

    cep = models.CharField(
        max_length=20
    )

    endereco = models.CharField(
        max_length=255
    )

    numero = models.CharField(
        max_length=20
    )

    complemento = models.CharField(
        max_length=255,
        blank=True
    )

    cidade = models.CharField(
        max_length=100
    )

    estado = models.CharField(
        max_length=2
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    pix_qr_code = models.TextField(
        blank=True,
        null=True
    )

    pix_qr_code_base64 = models.TextField(
        blank=True,
        null=True
    )

    pix_ticket_url = models.URLField(
        blank=True,
        null=True
    )

    email_pagamento_enviado = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f'Pedido #{self.codigo}'


# =====================================
    # ✅ MERCADO PAGO
    # =====================================

    metodo_pagamento = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    mercadopago_payment_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    mercadopago_status = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    bandeira_cartao = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    parcelas = models.PositiveIntegerField(
        default=1
    )

    nome = models.CharField(
        max_length=255
    )

    email = models.EmailField()

    telefone = models.CharField(
        max_length=20,
        blank=True
    )

    cpf = models.CharField(
        max_length=14,
        blank=True,
        null=True
    )

    cep = models.CharField(
        max_length=20
    )

    endereco = models.CharField(
        max_length=255
    )

    numero = models.CharField(
        max_length=20
    )

    complemento = models.CharField(
        max_length=255,
        blank=True
    )

    cidade = models.CharField(
        max_length=100
    )

    estado = models.CharField(
        max_length=2
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    atualizado_em = models.DateTimeField(
        auto_now=True
    )

    pix_qr_code = models.TextField(
        blank=True,
        null=True
    )

    pix_qr_code_base64 = models.TextField(
        blank=True,
        null=True
    )

    pix_ticket_url = models.URLField(
        blank=True,
        null=True
    )

    email_pagamento_enviado = models.BooleanField(
        default=False
    )
    
    def __str__(self):
        return f'Pedido #{self.codigo}'



class ItemPedido(models.Model):
    
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens'
    )

    perfume = models.ForeignKey(
        'produtos.Perfume',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    produto_nome = models.CharField(
        max_length=255
    )

    tamanho = models.CharField(
        max_length=50
    )

    quantidade = models.PositiveIntegerField()

    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    
    
    

    def __str__(self):
        return self.produto_nome