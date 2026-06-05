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

    imagem = models.ImageField(upload_to='perfumes/', blank=True, null=True)

    imagem_mobile = models.ImageField(
        upload_to='perfumes/mobile/', blank=True, null=True
    )

    imagem_descricao = models.ImageField(
        upload_to='perfumes/descricao/',
        blank=True,
        null=True
    )

    imagem_descricao_mobile = models.ImageField(
        upload_to='perfumes/descricao/mobile/',
        blank=True,
        null=True
    )

    # ✅ 🔥 ALTERAÇÃO AQUI
    categorias = models.ManyToManyField(Categoria)

    def __str__(self):
        return self.nome


class Preco(models.Model):
    perfume = models.ForeignKey(
        Perfume,
        related_name='precos',
        on_delete=models.CASCADE
    )
    tamanho = models.CharField(max_length=10)
    valor = models.DecimalField(max_digits=8, decimal_places=2)