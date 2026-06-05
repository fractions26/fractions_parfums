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

    # ✅ imagens agora são caminhos (sem upload)
    imagem = models.CharField(max_length=255, blank=True, null=True)
    imagem_descricao = models.CharField(max_length=255, blank=True, null=True)

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


class Preco(models.Model):
    perfume = models.ForeignKey(
        Perfume,
        related_name='precos',
        on_delete=models.CASCADE
    )
    tamanho = models.CharField(max_length=10)
    valor = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.perfume.nome} - {self.tamanho} - R$ {self.valor}"