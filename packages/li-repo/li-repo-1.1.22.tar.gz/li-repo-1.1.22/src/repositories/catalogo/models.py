# -*- coding: utf-8 -*-

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from mptt.models import MPTTModel, TreeForeignKey
from repositories.plataforma.models import Index


class Produto(models.Model):
    TIPO_NORMAL = 'normal'
    TIPO_ATRIBUTO = 'atributo'
    TIPO_VIRTUAL = 'virtual'
    TIPO_OPCAO = 'atributo_opcao'
    TIPO_KIT = 'kit'

    CHOICES_PRODUTO_TIPOS = [
        (TIPO_NORMAL, u'Produto simples'),
        (TIPO_ATRIBUTO, u'Produto com opções'),
        (TIPO_VIRTUAL, u'Produto virtual'),
        (TIPO_OPCAO, u'Opção'),
        (TIPO_KIT, u'Kit de produtos')
    ]

    id = models.AutoField(db_column='produto_id', primary_key=True)
    id_externo = models.IntegerField(db_column="produto_id_externo", null=True)

    modelo = models.CharField(db_column='produto_modelo', max_length=255, null=True, default=None)
    sku = models.CharField(db_column='produto_sku', max_length=255, null=True, default=None)
    ativo = models.BooleanField(db_column='produto_ativo', default=False)
    removido = models.BooleanField(db_column='produto_removido', default=False)
    peso = models.DecimalField(db_column='produto_peso', max_digits=16, decimal_places=3, default=None, null=True)
    altura = models.IntegerField(db_column='produto_altura', default=None, null=True)
    largura = models.IntegerField(db_column='produto_largura', default=None, null=True)
    profundidade = models.IntegerField(db_column='produto_comprimento', default=None, null=True)
    template = models.CharField(db_column='produto_template', max_length=255, null=True, default=None)
    tipo = models.CharField(db_column='produto_tipo', max_length=255, null=True)
    bloqueado = models.BooleanField(db_column='produto_bloqueado', default=False, null=False)
    usado = models.BooleanField(db_column='produto_usado', default=False, null=False)

    nome = models.CharField(db_column='produto_nome', max_length=255, default=None, null=True)
    url_video_youtube = models.CharField(db_column='produto_url_video_youtube', max_length=255, default=None, null=True)
    descricao_completa = models.TextField(db_column='produto_descricao_completa', default=None, null=True)

    imagens = models.ManyToManyField('plataforma.Imagem', through='ProdutoImagem')
    grades = models.ManyToManyField('catalogo.Grade', through='ProdutoGrade')
    categorias = models.ManyToManyField('catalogo.Categoria', through='ProdutoCategoria')
    destaque = models.BooleanField(db_column='produto_destaque', null=False, default=False)

    cache_imagem_principal = models.ForeignKey('plataforma.Imagem', db_column='produto_cache_imagem_principal_id', null=True, on_delete=models.SET_NULL)
    cache_url = models.CharField(db_column='produto_cache_url', max_length=255, null=True, default=None)

    pai = models.ForeignKey('catalogo.Produto', db_column='produto_id_pai', null=True)
    marca = models.ForeignKey('catalogo.Marca', null=True)
    conta = models.ForeignKey('plataforma.Conta')
    contrato = models.ForeignKey('plataforma.Contrato')

    class Meta:
        app_label = "catalogo"
        db_table = u"catalogo\".\"tb_produto"
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        unique_together = (("conta", "sku"),)
        get_latest_by = 'id'

    def get_absolute_url(self, usa_dominio=True):
        if self.cache_url:
            if usa_dominio:
                return "http://{}{}".format(self.conta.url_dominio, self.cache_url)
            return self.cache_url
        return None

    def atualizar_dados_elasticsearch(self):
        """Cria um faz update de uma row no ProdutoIndex"""
        if self.removido:
            self.remover_produto_elasticsearch()
        else:
            filtro = dict(produto_id=self.id, conta_id=self.conta_id)
            atualizados = Index.objects.filter(**filtro).update(status=2, status_alt=2)
            if not atualizados:
                Index.objects.create(status=2, status_alt=2, **filtro)


class Categoria(MPTTModel):
    id = models.AutoField(db_column="categoria_id", primary_key=True)
    id_externo = models.IntegerField(db_column="categoria_id_externo", null=True)

    ativa = models.BooleanField(db_column="categoria_ativa", default=True)
    quantidade_filhos = models.IntegerField(db_column="categoria_filhos", default=0)
    url = models.CharField(db_column="categoria_url", null=True, max_length=255)

    nome = models.CharField(db_column='categoria_nome', max_length=255)
    descricao = models.TextField(db_column='categoria_descricao', null=True)

    posicao = models.IntegerField(db_column="categoria_posicao", default=0)
    parent = TreeForeignKey("self", null=True, blank=True, related_name="children", on_delete=models.PROTECT)
    conta = models.ForeignKey('plataforma.Conta', db_column="conta_id")
    contrato = models.ForeignKey('plataforma.Contrato', db_column='contrato_id')

    class MPTTMeta:
        order_insertion_by = ['posicao']

    class Meta:
        db_table = u"catalogo\".\"tb_categoria"


class ProdutoCategoria(models.Model):
    """Relação entre produto e categoria."""
    id = models.AutoField(db_column='produto_categoria_id', primary_key=True)
    principal = models.BooleanField(db_column='produto_categoria_principal', default=False)

    produto = models.ForeignKey('catalogo.Produto', related_name='produto_categorias', on_delete=models.CASCADE)
    categoria = models.ForeignKey('catalogo.Categoria', related_name='produtos_categoria', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='produtos_categorias')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='produtos_categorias')

    class Meta:
        db_table = u"catalogo\".\"tb_produto_categoria"


class ProdutoImagem(models.Model):
    """Imagens de um produto."""
    id = models.AutoField(db_column='produto_imagem_id', primary_key=True)
    posicao = models.IntegerField(db_column='produto_imagem_posicao', null=True, default=None)
    principal = models.NullBooleanField(db_column='produto_imagem_principal', null=True, default=False)

    # Os related_name's são "produto_imagens" e "produtos_imagem" pois já existe
    # "imagens" e "produtos" dentro do produto e imagens, respectivamente,
    # referenciando ao ManyToMany de Produto x Imagem.
    produto = models.ForeignKey('catalogo.Produto', related_name='produto_imagens', on_delete=models.CASCADE)
    imagem = models.ForeignKey('domain.Imagem', related_name='produtos_imagem', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='produtos_imagens')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='produtos_imagens')

    class Meta:
        db_table = u'catalogo\".\"tb_produto_imagem'
        verbose_name = u'Imagem do produto'
        verbose_name_plural = u'Imagens dos produtos'
        ordering = ['produto', '-principal', 'posicao', 'id']


class ProdutoEstoque(models.Model):
    """Estoque de um produto."""
    SITUACAO_INDISPONIVEL = -1
    SITUACAO_DISPONIVEL = 0

    SITUACOES = [
        (SITUACAO_INDISPONIVEL, u'Indiponível'),
        (SITUACAO_DISPONIVEL, u'Diponível'),
    ]

    id = models.AutoField(db_column='produto_estoque_id', primary_key=True)
    gerenciado = models.BooleanField(db_column='produto_estoque_gerenciado', default=False)
    quantidade = models.DecimalField(db_column='produto_estoque_quantidade', max_digits=16, decimal_places=4, default=0)
    situacao_em_estoque = models.IntegerField(db_column='produto_estoque_situacao_em_estoque', default=0)
    situacao_sem_estoque = models.IntegerField(db_column='produto_estoque_situacao_sem_estoque', default=0)

    produto = models.OneToOneField('catalogo.Produto', related_name='estoque', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='produtos_estoque')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='produtos_estoques')

    class Meta:
        db_table = u"catalogo\".\"tb_produto_estoque"
        verbose_name = u'Estoque do Produto'
        verbose_name_plural = u"Estoque dos Produtos"
        ordering = ['id']

    def incrementar(self, quantidade=None, motivo=None):
        """Adiciona a quantidade passada a quantidade de itens no estoque."""
        self.quantidade = self.quantidade + quantidade
        self.save()

    def reduzir(self, quantidade=None, motivo=None, pedido_venda=None):
        """Reduz a quantidade de itens no estoque. Caso o pedido_venda seja
        enviado, a quantidade é descartada e o pedido_venda será usado para
        identificar a quantidade a ser reduzida.
        """
        if pedido_venda:
            pedido_item = pedido_venda.itens.get(produto=self.produto)
            quantidade = pedido_item.quantidade

        self.quantidade = self.quantidade - quantidade
        self.save()


@receiver(post_save, sender=ProdutoEstoque)
def produto_estoque_post_save(sender, instance, created, raw, **kwargs):
    if not created:
        instance.produto.atualizar_dados_elasticsearch()
