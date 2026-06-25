from django.db import models
from django.contrib.auth.models import User


class LoginLog(models.Model):

    email = models.EmailField()

    evento = models.CharField(
        max_length=50,
        default='LOGIN'
    )

    sucesso = models.BooleanField(
        default=False
    )

    ip = models.CharField(
        max_length=100,
        blank=True
    )

    user_agent = models.TextField(
        blank=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.email} - "
            f"{self.evento} - "
            f"{self.criado_em}"
        )


class PedidoLog(models.Model):
    
    pedido_id = models.IntegerField()

    codigo_pedido = models.CharField(
        max_length=20,
        blank=True
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    evento = models.CharField(
        max_length=100
    )

    observacao = models.TextField(
        blank=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"#{self.codigo_pedido} - "
            f"{self.evento}"
        )


class ErroLog(models.Model):

    url = models.TextField()

    erro = models.TextField()

    traceback = models.TextField()

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.erro[:60]


class CarrinhoAbandonadoLog(models.Model):
    
    usuario_email = models.EmailField(
        blank=True
    )

    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantidade_itens = models.IntegerField()

    checkout_em = models.DateTimeField()

    itens_removidos = models.BooleanField(
        default=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.usuario_email} - "
            f"R$ {self.valor_total}"
        )

class CheckoutVisitado(models.Model):
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    valor_total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantidade_itens = models.IntegerField()

    checkout_em = models.DateTimeField(
        auto_now_add=True
    )

    processado = models.BooleanField(
        default=False
    )

    # ✅ Compatibilidade com versão atual
    email_carrinho_enviado = models.BooleanField(
        default=False
    )

    email_carrinho_enviado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    # ✅ NOVO - EMAIL 1 HORA
    email_1_enviado = models.BooleanField(
        default=False
    )

    email_1_enviado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    # ✅ NOVO - EMAIL 24 HORAS
    email_2_enviado = models.BooleanField(
        default=False
    )

    email_2_enviado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    # ✅ NOVO - EMAIL 72 HORAS
    email_3_enviado = models.BooleanField(
        default=False
    )

    email_3_enviado_em = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.usuario.email if self.usuario else 'Sem usuário'} - "
            f"{self.checkout_em}"
        )

class AcessoPagina(models.Model):
    
    TIPO_CHOICES = (
        ('HOME', 'Home'),
        ('PRODUTO', 'Produto'),
        ('PEDIDO', 'Pedido'),
    )

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES
    )

    url = models.CharField(
        max_length=500,
        blank=True
    )

    ip = models.CharField(
        max_length=100,
        blank=True
    )

    criado_em = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Acesso Página'
        verbose_name_plural = 'Dashboard Geral'

    def __str__(self):
        return (
            f'{self.tipo} - '
            f'{self.criado_em:%d/%m/%Y %H:%M}'
        )