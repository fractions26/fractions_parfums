from django.db import models


class Categoria(models.Model):

    nome = models.CharField(max_length=50)

    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nome


class Perfume(models.Model):

    nome = models.CharField(max_length=150)

    marca = models.CharField(max_length=150)

    slug = models.SlugField(unique=True)

    # ✅ NOVO ESTOQUE EM ML
    estoque_ml = models.PositiveIntegerField(
        default=0,
        verbose_name="Estoque total em ML"
    )

    # ✅ CONTROLE ATIVO / INDISPONÍVEL
    ativo = models.BooleanField(
        default=True
    )

    # ✅ imagens agora são caminhos (sem upload)
    imagem = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    imagem_descricao = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    categorias = models.ManyToManyField(Categoria)

    def __str__(self):
        return self.nome

    # ✅ caminhos para exibir no template
    def get_imagem_url(self):

        if self.imagem:
            return f"/media/{self.imagem}"

        return ""

    def get_imagem_descricao_url(self):

        if self.imagem_descricao:
            return f"/media/{self.imagem_descricao}"

        return ""

    # ✅ verifica se possui estoque para determinado tamanho
    def disponivel_para(self, tamanho_ml):

        return self.estoque_ml >= tamanho_ml

    # ✅ calcula quantas unidades cabem no estoque
    def unidades_disponiveis(self, tamanho_ml):

        if tamanho_ml <= 0:
            return 0

        return self.estoque_ml // tamanho_ml


class Preco(models.Model):

    perfume = models.ForeignKey(
        Perfume,
        related_name='precos',
        on_delete=models.CASCADE
    )

    tamanho = models.CharField(max_length=10)

    valor = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )

    def __str__(self):

        return (
            f"{self.perfume.nome} - "
            f"{self.tamanho} - "
            f"R$ {self.valor}"
        )