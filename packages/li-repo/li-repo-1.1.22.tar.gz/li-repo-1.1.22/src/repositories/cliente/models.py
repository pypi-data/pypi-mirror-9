# -*- coding: utf-8 -*-
from django.core.exceptions import MultipleObjectsReturned

from django.db import models
from repositories.models import Pais


class ClienteGrupo(models.Model):
    """Grupo de clientes."""
    id = models.AutoField(db_column="cliente_grupo_id", primary_key=True)
    nome = models.CharField(db_column="cliente_grupo_nome", max_length=128)
    padrao = models.BooleanField(db_column="cliente_grupo_padrao", default=False)

    conta = models.ForeignKey("plataforma.Conta", related_name="grupos", on_delete=models.CASCADE, null=True, blank=True)
    contrato = models.ForeignKey("plataforma.Contrato", related_name="grupos")

    class Meta:
        db_table = u"cliente\".\"tb_cliente_grupo"
        verbose_name = u"Grupo de cliente"
        verbose_name_plural = u"Grupo de clientes"
        ordering = ["conta", "nome"]
        unique_together = (("conta", "nome"),)

    def __unicode__(self):
        return self.nome


class Cliente(models.Model):
    """Clientes da loja virtual."""

    CLIENTE_SITUACAO_APROVADO = 'aprovado'
    CLIENTE_SITUACAO_NEGADO = 'negado'
    CLIENTE_SITUACAO_PENDENTE = 'pendente'

    id = models.AutoField(db_column="cliente_id", primary_key=True)
    email = models.EmailField(db_column="cliente_email", max_length=255)
    senha = models.CharField(db_column="cliente_senha", max_length=64)
    nome = models.CharField(db_column="cliente_nome", max_length=255, null=True)
    sexo = models.CharField(db_column="cliente_sexo", max_length=1, null=True)
    telefone_principal = models.CharField(db_column="cliente_telefone_principal", max_length=11, null=True)
    telefone_comercial = models.CharField(db_column="cliente_telefone_comercial", max_length=11, null=True)
    telefone_celular = models.CharField(db_column="cliente_telefone_celular", max_length=11, null=True)
    newsletter = models.BooleanField(db_column="cliente_newsletter", default=True)
    data_nascimento = models.DateField(db_column="cliente_data_nascimento", null=True)
    data_criacao = models.DateTimeField(db_column="cliente_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="cliente_data_modificacao", auto_now=True)
    facebook_id = models.CharField(db_column='cliente_facebook_usuario_id', max_length=64, default=None, null=True)
    teste = models.BooleanField(db_column="cliente_teste", default=False, null=False)
    grupo = models.ForeignKey('cliente.ClienteGrupo', db_column="cliente_grupo_id", related_name="clientes")
    conta = models.ForeignKey("plataforma.Conta", related_name="clientes", on_delete=models.CASCADE)
    contrato = models.ForeignKey("plataforma.Contrato", related_name="clientes")
    situacao = models.CharField(db_column='cliente_situacao', max_length=32, default=CLIENTE_SITUACAO_PENDENTE, null=False)

    class Meta:
        app_label = "cliente"
        db_table = u"cliente\".\"tb_cliente"
        verbose_name = u"Cliente"
        verbose_name_plural = u"Clientes"
        ordering = ["email"]
        unique_together = (("conta", "email"),)
        get_latest_by = 'id'

    def __unicode__(self):
        return self.email

    @property
    def primeiro_nome(self):
        if self.nome:
            return self.nome.split()[0]

    @property
    def endereco(self):
        if not hasattr(self, '_endereco'):
            try:
                self._endereco = self.enderecos.get(principal=True)
            except (MultipleObjectsReturned, ClienteEndereco.DoesNotExist):
                try:
                    endereco_principal = self.enderecos.all()[0]
                except IndexError:
                    self._endereco = None
                else:
                    endereco_principal.principal = True
                    endereco_principal.save()
                    self._endereco = endereco_principal
        return self._endereco

    @property
    def eh_primeira_compra_na_loja(self):
        return len(self.pedidos.all()[:0]) > 0

    @property
    def eh_confiavel(self):
        return False


class ClienteFavorito(models.Model):

    id = models.AutoField(db_column="cliente_favorito_id", primary_key=True)
    cliente = models.ForeignKey('cliente.Cliente', db_column="cliente_id")
    codigo = models.CharField(db_column="cliente_favorito_codigo", null=True, blank=True, max_length=32)
    data_criacao = models.DateTimeField(db_column="cliente_favorito_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="cliente_favorito_data_modificacao", auto_now=True)

    produtos = models.ManyToManyField('catalogo.Produto', db_column="produto_id", related_name='favoritos', through='ClienteFavoritoProduto')
    conta = models.ForeignKey('plataforma.Conta', related_name='favoritos')
    contrato = models.ForeignKey("plataforma.Contrato", related_name="favoritos")

    class Meta:
        db_table = u"cliente\".\"tb_cliente_favorito"
        verbose_name = u"Favorito do cliente"
        verbose_name_plural = u"Favoritos dos clientes"
        ordering = ['data_criacao']


class ClienteFavoritoProduto(models.Model):

    id = models.AutoField(db_column="cliente_favorito_produto_id", primary_key=True)
    produto = models.ForeignKey('catalogo.Produto', db_column="produto_id", related_name='produtos_favoritos')
    favorito = models.ForeignKey('cliente.ClienteFavorito', db_column="cliente_favorito_id", related_name='produtos_favoritos')

    conta = models.ForeignKey('plataforma.Conta', related_name='produtos_favoritos')
    contrato = models.ForeignKey("plataforma.Contrato", related_name="produtos_favoritos")

    class Meta:
        db_table = u"cliente\".\"tb_cliente_favorito_produto"
        verbose_name = u"Produto favorito"
        verbose_name_plural = u"Produtos favoritos"


class ClienteEndereco(models.Model):
    """Endereços dos clientes."""
    ENDERECO_TIPOS = [
        ("PF", u"Pessoa Física"),
        ("PJ", u"Pessoa Jurídica"),
        ("IN", u"Internacional"),
    ]

    id = models.AutoField(db_column="cliente_endereco_id", primary_key=True)
    tipo = models.CharField(db_column="cliente_endereco_tipo", max_length=64, choices=ENDERECO_TIPOS, null=True, default=None)
    cpf = models.CharField(db_column="cliente_endereco_cpf", max_length=11, null=True, default=None)
    rg = models.CharField(db_column="cliente_endereco_rg", max_length=20, null=True, default=None)
    cnpj = models.CharField(db_column="cliente_endereco_cnpj", max_length=14, null=True, default=None)
    razao_social = models.CharField(db_column="cliente_endereco_razao_social", max_length=255, null=True, default=None)
    ie = models.CharField(db_column="cliente_endereco_ie", max_length=20, null=True, default=None)
    nome = models.CharField(db_column="cliente_endereco_nome", max_length=255)
    endereco = models.CharField(db_column="cliente_endereco_endereco", max_length=255)
    numero = models.CharField(db_column="cliente_endereco_numero", max_length=10)
    complemento = models.CharField(db_column="cliente_endereco_complemento", max_length=255, null=True)
    referencia = models.CharField(db_column="cliente_endereco_referencia", max_length=255, null=True)
    bairro = models.CharField(db_column="cliente_endereco_bairro", max_length=128)
    cidade = models.CharField(db_column="cliente_endereco_cidade", max_length=128)
    estado = models.CharField(db_column="cliente_endereco_estado", max_length=2)
    cep = models.CharField(db_column="cliente_endereco_cep", max_length=8)
    pais_extenso = models.CharField(db_column="cliente_endereco_pais", max_length=128, null=True)
    principal = models.BooleanField(db_column="cliente_endereco_principal", default=False)

    pais = models.ForeignKey(Pais, related_name="enderecos")
    cliente = models.ForeignKey('cliente.Cliente', related_name="enderecos", on_delete=models.CASCADE)
    conta = models.ForeignKey("plataforma.Conta", related_name="enderecos")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="enderecos")

    class Meta:
        db_table = u"cliente\".\"tb_cliente_endereco"
        verbose_name = u"Endereço do cliente"
        verbose_name_plural = u"Endereços do cliente"
        ordering = ["nome"]
        unique_together = (
            "tipo", "cpf", "rg", "cnpj", "razao_social", "ie", "nome",
            "endereco", "numero", "complemento", "bairro", "cidade",
            "estado", "cep", "pais", "cliente", "conta")
        get_latest_by = "id"

    def __unicode__(self):
        return self.nome


