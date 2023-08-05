# -*- coding: utf-8 -*-

from django.db import models
from jsonfield import JSONField
from django.utils.text import slugify


class Banco(models.Model):
    id = models.AutoField(db_column="banco_id", primary_key=True)
    nome = models.CharField(db_column="banco_nome", max_length=128)
    imagem = models.CharField(db_column='banco_imagem', max_length=256)
    codigo = models.CharField(db_column='banco_codigo', max_length=3)

    class Meta:
        db_table = u"configuracao\".\"tb_banco"
        verbose_name = u'Banco'
        verbose_name_plural = u'Bancos'
        ordering = ['nome']

    def __unicode__(self):
        return self.nome

    def natural_key(self):
        return self.nome


class BoletoCarteira(models.Model):
    id = models.AutoField(db_column="boleto_carteira_id", primary_key=True)

    numero = models.CharField(db_column="boleto_carteira_numero", max_length=32, null=False)
    nome = models.CharField(db_column="boleto_carteira_nome", max_length=128, null=False)
    convenio = models.BooleanField(db_column="boleto_carteira_convenio", default=False, null=False)
    ativo = models.BooleanField(db_column="boleto_carteira_ativo", default=False, null=False)

    banco = models.ForeignKey('configuracao.Banco', db_column="banco_id", related_name='carteiras')

    class Meta:
        db_table = u"configuracao\".\"tb_boleto_carteira"
        verbose_name = u'Carteira de boleto'
        verbose_name_plural = u'Carteiras de boletos'
        unique_together = (('banco', 'numero', 'convenio'),)

    def __unicode__(self):
        return self.nome


class Parcela(models.Model):
    id = models.AutoField(db_column="pagamento_parcela_id", primary_key=True)
    numero_parcelas = models.IntegerField(db_column="pagamento_parcela_numero_parcelas")
    fator = models.DecimalField(db_column="pagamento_parcela_fator", max_digits=16, decimal_places=6)

    forma_pagamento = models.ForeignKey('configuracao.FormaPagamento', db_column="pagamento_id", related_name="parcelas")

    class Meta:
        db_table = u"configuracao\".\"tb_pagamento_parcela"
        verbose_name = u'Parcela'
        verbose_name_plural = u"Parcelas"
        ordering = ['id']


class FormaPagamento(models.Model):
    """Forma de pagamento."""

    CODIGOS_GATEWAYS = ['pagseguro', 'pagamento_digital', 'mercadopago', 'paypal', 'mercado_pago']

    PRINCIPAIS_FORMAS_PAGAMENTO = {
        'pagamento_digital': {
            'cartoes': ['visa', 'mastercard', 'hipercard', 'amex'],
            'bancos': ['itau', 'bradesco', 'banco-do-brasil'],
            'outros': ['boleto']
        },
        'pagseguro': {
            'cartoes': ['visa', 'mastercard', 'hipercard', 'amex'],
            'bancos': ['itau', 'bradesco', 'banco-do-brasil'],
            'outros': ['boleto']
        },
        'paypal': {
            'cartoes': ['visa', 'mastercard', 'amex']
        },
        'mercadopago': {
            'cartoes': ['visa', 'mastercard', 'amex', 'elo'],
            'outros': ['boleto']
        },
        'mercado_pago': {
            'cartoes': ['visa', 'mastercard', 'amex', 'elo'],
            'outros': ['boleto']
        }
    }

    id = models.AutoField(db_column="pagamento_id", primary_key=True)
    nome = models.CharField(db_column="pagamento_nome", max_length=128)
    codigo = models.CharField(db_column="pagamento_codigo", max_length=128, unique=True)
    ativo = models.BooleanField(db_column="pagamento_ativado", default=False)
    valor_minimo_parcela = models.DecimalField(db_column='pagamento_parcela_valor_minimo_parcela', max_digits=16, decimal_places=2, null=True)
    valor_minimo_parcelamento = models.DecimalField(db_column='pagamento_parcela_valor_minimo', max_digits=16, decimal_places=2, null=True)
    plano_indice = models.IntegerField(db_column='pagamento_plano_indice', default=1)
    posicao = models.IntegerField(db_column='pagamento_posicao', default=1000, null=False)

    conta = models.ForeignKey("plataforma.Conta", related_name="formas_pagamentos", null=True, default=None)
    contrato = models.ForeignKey("plataforma.Contrato", related_name="formas_pagamentos", null=True, default=None)

    class Meta:
        app_label = 'configuracao'
        db_table = u"configuracao\".\"tb_pagamento"
        verbose_name = u"Forma de pagamento"
        verbose_name_plural = u"Formas de pagamentos"
        ordering = ["posicao", "nome"]

    def __unicode__(self):
        return self.nome


class PagamentoBanco(models.Model):

    id = models.AutoField(db_column="pagamento_banco_id", primary_key=True)
    agencia = models.CharField(db_column="pagamento_banco_agencia", max_length=11, null=False)
    numero_conta = models.CharField(db_column="pagamento_banco_conta", max_length=11, null=False)
    poupanca = models.BooleanField(db_column="pagamento_banco_poupanca", default=True, null=False)
    operacao = models.CharField(db_column="pagamento_banco_variacao", max_length=10, null=True)
    favorecido = models.CharField(db_column="pagamento_banco_favorecido", max_length=256)
    cpf = models.CharField(db_column="pagamento_banco_cpf", max_length=11, null=True)
    cnpj = models.CharField(db_column="pagamento_banco_cnpj", max_length=14, null=True)
    ativo = models.BooleanField(db_column="pagamento_banco_ativo", null=False, default=False)

    banco = models.ForeignKey('configuracao.Banco', db_column="banco_id", related_name='bancos_pagamentos')
    conta = models.ForeignKey('plataforma.Conta', related_name='pagamento_bancos')
    pagamento = models.ForeignKey('configuracao.FormaPagamento', db_column="pagamento_id", related_name='bancos')
    contrato = models.ForeignKey("plataforma.Contrato", related_name="pagamento_bancos")

    class Meta:
        db_table = u"configuracao\".\"tb_pagamento_banco"
        verbose_name = u'Banco para depósito'
        verbose_name_plural = u'Bancos para depósito'
        unique_together = (('banco', 'conta'),)

    def __unicode__(self):
        return unicode(self.banco.nome)

    def __repr__(self):
        return slugify(self.banco.nome)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(PagamentoBanco, self).save(*args, **kwargs)

    @property
    def cpf_cnpj(self):
        return self.cpf or self.cnpj or None


class FormaPagamentoConfiguracao(models.Model):
    """Configuração da forma de pagamento."""
    TIPO_VALOR_FIXO = 'fixo'
    TIPO_PORCENTAGEM = 'porcentagem'

    id = models.AutoField(db_column="pagamento_configuracao_id", primary_key=True)
    usuario = models.CharField(db_column="pagamento_configuracao_usuario", max_length=128, null=True)
    senha = models.CharField(db_column="pagamento_configuracao_senha", max_length=128, null=True)
    token = models.CharField(db_column="pagamento_configuracao_token", max_length=128, null=True)
    token_expiracao = models.DateTimeField(db_column="pagamento_configuracao_token_expiracao", null=True)
    assinatura = models.CharField(db_column="pagamento_configuracao_assinatura", max_length=128, null=True)
    codigo_autorizacao = models.CharField(db_column="pagamento_configuracao_codigo_autorizacao", max_length=128, null=True)
    usar_antifraude = models.BooleanField(db_column='pagamento_configuracao_usar_antifraude', null=True, default=False)
    aplicacao = models.CharField(db_column="pagamento_configuracao_aplicacao_id", max_length=128, null=True, default=None)
    ativo = models.BooleanField(db_column="pagamento_configuracao_ativo", default=False)
    mostrar_parcelamento = models.BooleanField(db_column='pagamento_coonfiguracao_mostrar_parcelamento', default=False, null=False)
    maximo_parcelas = models.IntegerField(db_column="pagamento_configuracao_quantidade_parcela_maxima", default=None, null=True)
    parcelas_sem_juros = models.IntegerField(db_column="pagamento_configuracao_quantidade_parcela_sem_juros", default=None, null=True)
    desconto = models.BooleanField(db_column="pagamento_configuracao_desconto", default=False, null=False)
    desconto_tipo = models.CharField(db_column="pagamento_configuracao_desconto_tipo", max_length=32, default=TIPO_PORCENTAGEM)
    desconto_valor = models.DecimalField(db_column='pagamento_configuracao_desconto_valor', max_digits=16, decimal_places=2, null=True)
    juros_valor = models.DecimalField(db_column='pagamento_configuracao_juros_valor', max_digits=16, decimal_places=6, null=True)
    email_comprovante = models.EmailField(db_column='pagamento_configuracao_email_comprovante', null=True)
    informacao_complementar = models.TextField(db_column='pagamento_configuracao_informacao_complementar', null=True)
    aplicar_no_total = models.BooleanField(db_column='pagamento_configuracao_desconto_aplicar_no_total', null=False, default=False)
    valor_minimo_aceitado = models.DecimalField(db_column='pagamento_configuracao_valor_minimo_aceitado', max_digits=16, decimal_places=2, null=True)
    valor_minimo_parcela = models.DecimalField(db_column='pagamento_configuracao_valor_minimo_parcela', max_digits=16, decimal_places=2, null=True)

    json = JSONField(db_column='pagamento_configuracao_json', null=True, default=None)

    forma_pagamento = models.ForeignKey('configuracao.FormaPagamento', db_column="pagamento_id", related_name="configuracoes")
    conta = models.ForeignKey("plataforma.Conta", related_name="formas_pagamentos_configuracoes")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="formas_pagamentos_configuracoes")

    data_criacao = models.DateTimeField(db_column='pagamento_configuracao_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='pagamento_configuracao_data_modificacao', null=True, auto_now=True)

    class Meta:
        db_table = u"configuracao\".\"tb_pagamento_configuracao"
        verbose_name = u"Configuração da forma de pagamento"
        verbose_name_plural = u"Configurações das formas de pagamentos"
        ordering = ["id"]
        unique_together = (("conta", "forma_pagamento"),)

    def __unicode__(self):
        return unicode(self.id)


class Envio(models.Model):
    """Formas de envios."""
    id = models.AutoField(db_column="envio_id", primary_key=True)
    nome = models.CharField(db_column="envio_nome", max_length=128)
    codigo = models.CharField(db_column="envio_codigo", max_length=128)

    class Meta:
        app_label = "configuracao"
        db_table = u"configuracao\".\"tb_envio"
        ordering = ["posicao", "nome"]
        unique_together = (("nome", "codigo", "conta"),)

    def __unicode__(self):
        return self.nome
