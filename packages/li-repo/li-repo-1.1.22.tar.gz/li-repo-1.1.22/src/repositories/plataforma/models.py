# -*- coding: utf-8 -*-

from django.db import models
from jsonfield import JSONField


class Contrato(models.Model):

    id = models.AutoField(db_column="contrato_id", primary_key=True)
    nome = models.CharField(db_column="contrato_nome", max_length=255)
    ativo = models.BooleanField(db_column="contrato_ativo", default=True)
    codigo = models.CharField(db_column="contrato_codigo", max_length=255, unique=True)
    dominio = models.CharField(db_column="contrato_dominio", max_length=255)
    url_institucional = models.CharField(db_column="contrato_url_institucional", max_length=255)
    parametros = JSONField(u'Parametros do contrato', db_column="contrato_parametros", null=True)
    tipo = models.CharField(db_column="contrato_tipo", max_length=32)

    data_inicio = models.DateField(db_column='contrato_data_inicio')
    dia_vencimento = models.IntegerField(default=None, null=True, db_column='contrato_dia_vencimento', blank=True)

    minimo_mensal_valor = models.DecimalField(db_column="contrato_minimo_mensal_valor", max_digits=16, decimal_places=2, null=0.00)
    minimo_mensal_inicio_em_meses = models.IntegerField(db_column="contrato_minimo_mensal_inicio_em_meses", null=True, default=0)

    razao_social = models.CharField(db_column="contrato_razao_social", max_length=255)
    tipo_pessoa = models.CharField(db_column="contrato_tipo_pessoa", max_length=2, null=True, default='PJ')
    cpf_cnpj = models.CharField(db_column="contrato_cpf_cnpj", max_length=15, null=True, default=None)
    nome_responsavel = models.CharField(db_column="contrato_nome_responsavel", max_length=128, null=True, default=None)
    email_nota_fiscal = models.CharField(db_column="contrato_email_nota_fiscal", max_length=128, null=True, default=None)
    telefone_principal = models.CharField(db_column="contrato_telefone_principal", max_length=11, null=True, default=None)
    telefone_celular = models.CharField(db_column="contrato_telefone_celular", max_length=11, null=True, default=None)
    endereco_logradouro = models.CharField(db_column="contrato_endereco_logradouro", max_length=128, null=True, default=None)
    endereco_numero = models.CharField(db_column="contrato_endereco_numero", max_length=32, null=True, default=None)
    endereco_complemento = models.CharField(db_column="contrato_endereco_complemento", max_length=128, null=True, default=None)
    endereco_bairro = models.CharField(db_column="contrato_endereco_bairro", max_length=50, null=True, default=None)
    endereco_cep = models.CharField(db_column="contrato_endereco_cep", max_length=8, null=True, default=None)
    endereco_cidade_ibge = models.IntegerField(db_column="contrato_endereco_cidade_ibge", null=True, default=None)
    endereco_estado = models.CharField(u'Estado', db_column="contrato_endereco_estado", max_length=2, null=True, default=None)

    url_termo = models.TextField(db_column="contrato_url_termo", null=True, default=None)
    headtags = models.TextField(db_column="contrato_headtags", null=True, default=None)

    colecao = models.ForeignKey('faturamento.Colecao', db_column="colecao_id")

    class Meta:
        app_label = 'plataforma'
        db_table = u"plataforma\".\"tb_contrato"


class Conta(models.Model):

    CONTA_SITUACOES = [
        ('ATIVA','Loja ATIVA'),
        ('BLOQUEADA','Loja BLOQUEADA'),
        ('CANCELADA','Loja CANCELADA')
    ]

    id = models.AutoField(db_column="conta_id", primary_key=True)
    apelido = models.CharField(db_column="conta_apelido", max_length=32)
    nome = models.CharField(db_column="conta_loja_nome", max_length=128, null=False)
    email = models.CharField(db_column="conta_loja_email", max_length=128, null=True, default=None)
    dominio = models.CharField(db_column="conta_loja_dominio", max_length=128, null=True, default=None)
    situacao = models.CharField(db_column="conta_situacao", max_length=32, null=False, default='ATIVA', choices=CONTA_SITUACOES)

    habilitar_facebook = models.BooleanField(db_column='conta_habilitar_facebook', default=False)
    habilitar_mercadolivre = models.BooleanField(db_column='conta_habilitar_mercadolivre', default=False)
    habilitar_mobile = models.BooleanField(db_column='conta_habilitar_mobile', default=True)

    contrato = models.ForeignKey('Contrato', db_column="contrato_id")
    plano = models.ForeignKey('faturamento.Plano', db_column="plano_id")

    class Meta:
        app_label = 'plataforma'
        db_table = u"plataforma\".\"tb_conta"

    @property
    def url_dominio(self):
        if self.dominio:
            return self.dominio
        else:
            return self.url_subdominio

    @property
    def url_subdominio_facebook(self):
        return "%s-facebook.%s" % (self.apelido, self.contrato.dominio)

    @property
    def url_subdominio(self):
        return "%s.%s" % (self.apelido, self.contrato.dominio)

    @property
    def email_contato(self):
        if self.email:
            return self.email
        try:
            return self.usuarios.all()[0].email
        except IndexError:
            return None


class Dominio(models.Model):
    """Lista de domínios habilitados para uma conta."""
    id = models.AutoField(db_column="dominio_id", primary_key=True)
    fqdn = models.CharField(db_column="dominio_fqdn", max_length=128, null=False, unique=True)
    principal = models.BooleanField(db_column="dominio_principal", default=False, db_index=True)

    conta = models.ForeignKey("Conta", db_column="conta_id", related_name="dominios")

    class Meta:
        db_table = u"configuracao\".\"tb_dominio"


class Usuario(models.Model):

    id = models.AutoField(db_column="usuario_id", primary_key=True)
    nome = models.CharField(db_column="usuario_nome", max_length=128)
    email = models.EmailField(db_column="usuario_email")
    confirmado = models.BooleanField(db_column="usuario_confirmado", default=False)

    conta_id = models.ManyToManyField('Conta', related_name="usuarios", through="ContaUsuario")

    class Meta:
        db_table = u"plataforma\".\"tb_usuario"

    @property
    def primeiro_nome(self):
        if self.nome:
            return self.nome.split()[0]


class ContaUsuario(models.Model):
    """Relação entre conta e usuário."""
    id = models.AutoField(db_column="conta_usuario_id", primary_key=True)

    usuario = models.ForeignKey('Usuario', db_column="usuario_id")
    conta = models.ForeignKey('Conta', db_column="conta_id")

    class Meta:
        db_table = u"plataforma\".\"tb_conta_usuario"
        unique_together = ('conta', 'usuario')


class Certificado(models.Model):
    """Tipo de certificados a venda."""

    id = models.AutoField(db_column="certificado_id", primary_key=True)
    ativo = models.BooleanField(db_column="certificado_ativo", default=True)
    nome = models.CharField(db_column="certificado_nome", max_length=64)
    codigo = models.CharField(db_column="certificado_codigo", max_length=64, unique=True)
    fornecedor = models.CharField(db_column="certificado_fornecedor", max_length=128)
    fornecedor_site = models.CharField(db_column="certificado_fornecedor_site", max_length=256, null=True)
    descricao = models.TextField(db_column="certificado_descricao", null=True, default=None)
    valor = models.DecimalField(db_column="certificado_valor", max_digits=16, decimal_places=2)
    validade_anos = models.IntegerField(db_column="certificado_validade_anos")

    crt_intermediario = models.TextField(db_column="certificado_crt_intermediario", null=True)
    crt_raiz = models.TextField(db_column="certificado_crt_raiz", null=True)

    class Meta:
        db_table = u"plataforma\".\"tb_certificado"

    def __unicode__(self):
        return self.nome


class ContaCertificado(models.Model):
    """Gerencia os Certificados SSL instalados na Loja integrada."""

    id = models.AutoField(db_column="conta_certificado_id", primary_key=True, null=False)
    dominio = models.CharField(db_column="conta_certificado_dominio", max_length=128)
    key = models.TextField(db_column="conta_certificado_key", null=True)
    csr = models.TextField(db_column="conta_certificado_csr", null=True)
    crt = models.TextField(db_column="conta_certificado_crt", null=True)
    data_inicio = models.DateTimeField(db_column="conta_certificado_data_inicio", auto_now_add=True)
    data_expiracao = models.DateTimeField(db_column="conta_certificado_data_expiracao", null=True)
    situacao = models.CharField(db_column="conta_certificado_situacao", max_length=32)

    nc_compra_id = models.IntegerField(db_column="conta_certificado_namecheap_compra_id", null=True)
    nc_certificado_id = models.IntegerField(db_column="conta_certificado_namecheap_certificado_id", null=True)
    nc_transacao_id = models.IntegerField(db_column="conta_certificado_namecheap_transacao_id", null=True)

    confirmacoes = models.IntegerField(db_column="conta_certificado_confirmacoes", null=False, default=0)

    certificado = models.ForeignKey('Certificado', related_name='contas', on_delete=models.CASCADE)
    contrato = models.ForeignKey('Contrato', db_column="contrato_id")
    conta = models.ForeignKey('Conta', db_column="conta_id")

    class Meta:
        db_table = u"plataforma\".\"tb_conta_certificado"


class Imagem(models.Model):
    """Imagens."""

    id = models.AutoField(db_column="imagem_id", primary_key=True)
    tabela = models.CharField(db_column="imagem_tabela", max_length=64, null=True)
    campo = models.CharField(db_column="imagem_campo", max_length=64, null=True)
    linha_id = models.IntegerField(db_column="imagem_linha_id", null=True)
    data_criacao = models.DateTimeField(db_column="imagem_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="imagem_data_modificacao", auto_now=True)

    caminho = models.CharField(db_column="imagem_caminho", null=True)

    tipo = models.CharField(db_column="imagem_tipo", max_length=32)
    processada = models.BooleanField(db_column="imagem_processada")

    contrato = models.ForeignKey('Contrato', db_column="contrato_id")
    conta = models.ForeignKey('Conta', db_column="conta_id")

    class Meta:
        db_table = u"plataforma\".\"tb_imagem"


class Index(models.Model):
    id = models.AutoField(db_column="index_id", primary_key=True)
    status = models.IntegerField(db_column="index_status", default=1, null=False)
    status_alt = models.IntegerField(db_column="index_status_alt", default=1, null=False)
    produto = models.ForeignKey("catalogo.Produto", related_name='produto_index', null=True)
    categoria = models.ForeignKey("catalogo.Categoria", related_name='categoria_indexar', null=True)
    data_atualizacao = models.DateTimeField(db_column="index_data_atualizacao", auto_now=True)
    conta = models.ForeignKey('plataforma.Conta', related_name='conta_indexar')
    mensagem_erro = models.TextField(db_column="index_mensagem_erro", null=True)

    class Meta:
        db_table = u"plataforma\".\"tb_index"
        verbose_name = u'Indexar'
        verbose_name_plural = u"Indexar"

    def indexado(self):
        self.status = 0
        self.save()

    def erro(self, msg):
        self.status = 1
        self.status_alt = 1
        self.mensagem_erro = msg
        self.save()
