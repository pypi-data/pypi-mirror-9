# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.aggregates import Max
from jsonfield import JSONField
from repositories.cliente.models import ClienteEndereco


class PedidoVendaSituacao(models.Model):
    """Situação de pedido de venda."""
    SITUACAO_AGUARDANDO_PAGTO = 2
    SITUACAO_PAGTO_EM_ANALISE = 3
    SITUACAO_PEDIDO_PAGO = 4
    SITUACAO_PAGTO_EM_DISPUTA = 6
    SITUACAO_PAGTO_DEVOLVIDO = 7
    SITUACAO_PEDIDO_CANCELADO = 8
    SITUACAO_PEDIDO_EFETUADO = 9
    SITUACAO_PEDIDO_ENVIADO = 11
    SITUACAO_PRONTO_RETIRADA = 13
    SITUACAO_PEDIDO_ENTREGUE = 14
    SITUACAO_PEDIDO_EM_SEPARACAO = 15
    SITUACAO_PAGTO_CHARGEBACK = 16

    id = models.AutoField(db_column="pedido_venda_situacao_id", primary_key=True)
    nome = models.CharField(db_column="pedido_venda_situacao_nome", max_length=64)
    codigo = models.CharField(db_column="pedido_venda_situacao_codigo", max_length=64)
    aprovado = models.BooleanField(db_column="pedido_venda_situacao_aprovado", default=False)
    cancelado = models.BooleanField(db_column="pedido_venda_situacao_cancelado", default=False)
    final = models.BooleanField(db_column="pedido_venda_situacao_final", default=False)
    padrao = models.BooleanField(db_column="pedido_venda_situacao_padrao", default=False)
    notificar_comprador = models.BooleanField(db_column="pedido_venda_situacao_notificar_comprador", default=False)
    ativo = models.BooleanField(db_column="pedido_venda_situacao_ativo", default=False)
    data_criacao = models.DateTimeField(db_column="pedido_venda_situacao_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="pedido_venda_situacao_data_modificacao", auto_now=True)

    conta = models.ForeignKey('plataforma.Conta', related_name='pedido_venda_situacoes', null=True, default=None)
    contrato = models.ForeignKey('plataforma.Contrato', related_name='pedido_venda_situacoes', null=True, default=None)

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_situacao"
        verbose_name = u'Situação do pedido de venda'
        verbose_name_plural = u"Situações de pedidos de vendas"
        ordering = ['nome']
        unique_together = (("conta", "nome"),)

    def __unicode__(self):
        return self.nome


class PedidoVendaSituacaoHistorico(models.Model):
    """Histórico de situações de um pedido de venda.

    O alterado_por pode receber três valores básicos:
        cliente - Quando foi o cliente que alterou.
        gateway - Quando a alteração foi feita pelo gateway de pagamento.
        usuario - Sempre que o usuário alterar a situação.
        sistema - Quando não é possível identificar quem fez a alteração.
    """
    ALTERADO_POR_CLIENTE = 'cliente'
    ALTERADO_POR_GATEWAY = 'gateway'
    ALTERADO_POR_USUARIO = 'usuario'
    ALTERADO_POR_SISTEMA = 'sistema'

    CHOICES_ALTERADO_POR = [
        (ALTERADO_POR_CLIENTE, u'Cliente'),
        (ALTERADO_POR_GATEWAY, u'Gateway'),
        (ALTERADO_POR_USUARIO, u'Usuário'),
        (ALTERADO_POR_SISTEMA, u'Sistema'),
    ]

    id = models.AutoField(db_column="pedido_venda_situacao_historico_id", primary_key=True)
    data = models.DateTimeField(db_column="pedido_venda_situacao_historico_data", auto_now=True)
    alterado_por = models.CharField(db_column="pedido_venda_situacao_historico_alterado_por", max_length=64, null=True, choices=CHOICES_ALTERADO_POR)
    alterado_por_nome = models.CharField(db_column="pedido_venda_situacao_historico_alterado_por_nome", max_length=128, null=True)

    situacao_inicial = models.ForeignKey('pedido.PedidoVendaSituacao', db_column="pedido_venda_situacao_id_inicial", related_name='pedido_venda_situacao_inicial_historico')
    situacao_final = models.ForeignKey('pedido.PedidoVendaSituacao', db_column="pedido_venda_situacao_id_final", related_name='pedido_venda_situacao_final_historico')
    pedido = models.ForeignKey('pedido.PedidoVenda', db_column='pedido_venda_id', related_name='historico', on_delete=models.CASCADE)
    conta = models.ForeignKey('plataforma.Conta', related_name='pedido_venda_situacao_historico')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='pedido_venda_situacao_historico')

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_situacao_historico"
        verbose_name = u'Histórico de situações de um pedido de venda'
        verbose_name_plural = u"Histórico de situações dos pedidos de vendas"
        ordering = ['id']

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(PedidoVendaSituacaoHistorico, self).save(*args, **kwargs)


class PedidoVendaTipo(models.Model):
    """Tipo de pedido de venda."""
    id = models.AutoField(db_column="pedido_venda_tipo_id", primary_key=True)
    nome = models.CharField(db_column="pedido_venda_tipo_nome", max_length=64)

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_tipo"
        verbose_name = u'Tipo de pedido de venda'
        verbose_name_plural = u"Tipos de pedidos de vendas"
        ordering = ['nome']

    def __unicode__(self):
        return self.nome


class PedidoVendaEndereco(models.Model):
    """Endereço de um pedido de venda. Esta é basicamente uma cópia da tabela
    de endereço do CRM.

    Esta cópia dos dados serve como cache para que não altere o endereço caso
    o cliente altere qualquer depois de criar o pedido de venda.
    """
    ENDERECO_TIPOS = [
        ("pf", u"Pessoa Física"),
        ("pj", u"Pessoa Jurídica"),
    ]

    id = models.AutoField(db_column="pedido_venda_endereco_id", primary_key=True)
    tipo = models.CharField(db_column="pedido_venda_endereco_tipo", max_length=64, choices=ENDERECO_TIPOS)
    cpf = models.CharField(db_column="pedido_venda_endereco_cpf", max_length=11, null=True)
    rg = models.CharField(db_column="pedido_venda_endereco_rg", max_length=20, null=True)
    cnpj = models.CharField(db_column="pedido_venda_endereco_cnpj", max_length=14, null=True)
    razao_social = models.CharField(db_column="pedido_venda_endereco_razao_social", max_length=255, null=True)
    ie = models.CharField(db_column="pedido_venda_endereco_ie", max_length=20, null=True)
    nome = models.CharField(db_column="pedido_venda_endereco_nome", max_length=255, null=False, blank=False)
    endereco = models.CharField(db_column="pedido_venda_endereco_endereco", max_length=255, null=False, blank=False)
    numero = models.CharField(db_column="pedido_venda_endereco_numero", max_length=10, null=False, blank=False)
    complemento = models.CharField(db_column="pedido_venda_endereco_complemento", max_length=255, null=True)
    referencia = models.CharField(db_column="pedido_venda_endereco_referencia", max_length=255, null=True)
    bairro = models.CharField(db_column="pedido_venda_endereco_bairro", max_length=128, null=False, blank=False)
    cidade = models.CharField(db_column="pedido_venda_endereco_cidade", max_length=128, null=False, blank=False)
    estado = models.CharField(db_column="pedido_venda_endereco_estado", max_length=2, null=False, blank=False)
    cep = models.CharField(db_column="pedido_venda_endereco_cep", max_length=8, null=False, blank=False)
    pais = models.CharField(db_column="pedido_venda_endereco_pais", max_length=128, null=True)

    conta = models.ForeignKey("plataforma.Conta", related_name="pedido_venda_enderecos")
    contrato = models.ForeignKey("plataforma.Contrato", related_name="pedido_venda_enderecos")

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_endereco"
        verbose_name = u'Endereço do pedido de venda'
        verbose_name_plural = u"Endereços de pedidos de vendas"
        ordering = ['id']

    def __unicode__(self):
        return unicode(self.id)


class PedidoVendaFormaEnvio(models.Model):
    """Forma de envio de um pedido de venda."""
    id = models.AutoField(db_column="pedido_venda_envio_id", primary_key=True)
    objeto = models.CharField(db_column="pedido_venda_envio_objeto", max_length=32, null=True)
    valor = models.DecimalField(db_column="pedido_venda_envio_valor", max_digits=16, decimal_places=2, null=True)
    data_criacao = models.DateTimeField(db_column="pedido_venda_envio_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="pedido_venda_envio_data_modificacao", auto_now=True)
    mensagem_correios = models.TextField(db_column="pedido_venda_envio_mensagem_correios", null=True, default=None)
    prazo = models.IntegerField(db_column='pedido_venda_envio_prazo', null=True, default=None)

    pedido = models.ForeignKey('pedido.PedidoVenda', db_column='pedido_venda_id', related_name='pedido_envios')
    envio = models.ForeignKey('configuracao.Envio', related_name='pedidos_envio')
    conta = models.ForeignKey('plataforma.Conta', related_name='pedido_venda_envios')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='pedido_venda_envios')

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_envio"
        verbose_name = u'Forma de envio de um pedido de venda'
        verbose_name_plural = u"Formas de envios dos pedidos de vendas"
        ordering = ['id']

    def __unicode__(self):
        return unicode(self.id)


class PedidoVendaFormaPagamento(models.Model):
    """Forma de pagamento de um pedido de venda."""
    id = models.AutoField(db_column="pedido_venda_pagamento_id", primary_key=True)
    valor = models.DecimalField(db_column="pedido_venda_pagamento_valor", max_digits=16, decimal_places=2, null=True)
    valor_pago = models.DecimalField(db_column="pedido_venda_pagamento_valor_pago", max_digits=16, decimal_places=2, null=True)
    transacao_id = models.CharField(db_column="pedido_venda_pagamento_transacao_id", max_length=64, null=True)
    identificador_id = models.CharField(db_column="pedido_venda_pagamento_identificador_id", max_length=64, null=True)
    conteudo = models.TextField(db_column="pedido_venda_pagamento_conteudo", null=True)
    conteudo_json = JSONField(db_column="pedido_venda_pagamento_conteudo_json", null=True)
    data_criacao = models.DateTimeField(db_column="pedido_venda_pagamento_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="pedido_venda_pagamento_data_modificacao", auto_now=True)
    pagamento_externo = models.BooleanField(db_column="pedido_venda_pagamento_pagamento_externo", null=False, default=False)

    banco = models.ForeignKey('configuracao.PagamentoBanco', db_column='pagamento_banco_id', related_name='pedidos_banco', null=True, default=None)
    pedido = models.ForeignKey('pedido.PedidoVenda', db_column='pedido_venda_id', related_name='pedido_pagamentos')
    pagamento = models.ForeignKey('configuracao.FormaPagamento', related_name='pedidos_pagamento')
    conta = models.ForeignKey('plataforma.Conta', related_name='pedido_venda_pagamentos')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='pedido_venda_pagamentos')

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_pagamento"
        verbose_name = u'Forma de pagamento de um pedido de venda'
        verbose_name_plural = u"Formas de pagamentos dos pedidos de vendas"
        ordering = ['id']
        unique_together = (("transacao_id", "identificador_id"), )

    def __unicode__(self):
        return unicode(self.id)


class PedidoVenda(models.Model):
    """Pedido de venda."""

    MAXIMO_DIAS_PEDIDO = 6

    id = models.AutoField(db_column='pedido_venda_id', primary_key=True)
    numero = models.BigIntegerField(db_column='pedido_venda_numero', null=False, db_index=True)
    consolidado = models.BooleanField(db_column='pedido_venda_consolidado', default=False)

    telefone_principal = models.CharField(db_column='pedido_venda_telefone_principal', max_length=11, null=True)
    telefone_comercial = models.CharField(db_column='pedido_venda_telefone_comercial', max_length=11, null=True)
    telefone_celular = models.CharField(db_column='pedido_venda_telefone_celular', max_length=11, null=True)

    valor_subtotal = models.DecimalField(db_column='pedido_venda_valor_subtotal', max_digits=16, decimal_places=4, null=True)
    valor_envio = models.DecimalField(db_column='pedido_venda_valor_envio', max_digits=16, decimal_places=4, null=True)
    valor_total = models.DecimalField(db_column='pedido_venda_valor_total', max_digits=16, decimal_places=4, null=True)
    valor_desconto = models.DecimalField(db_column='pedido_venda_valor_desconto', max_digits=16, decimal_places=4, null=True)
    peso_real = models.DecimalField(db_column='pedido_venda_peso_real', max_digits=16, decimal_places=3, null=True)

    data_criacao = models.DateTimeField(db_column='pedido_venda_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='pedido_venda_data_modificacao', auto_now=True)
    data_expiracao = models.DateTimeField(db_column='pedido_venda_data_expiracao', null=True, default=None)

    # Relacionada a Nota Fiscal
    conteudo_json = JSONField(db_column="pedido_venda_conteudo_json", null=True)
    numero_nota_fiscal = models.BigIntegerField(db_column="pedido_venda_numero_nota_fiscal", null=True)

    _endereco_entrega = models.OneToOneField('pedido.PedidoVendaEndereco', db_column='pedido_venda_endereco_entrega_id', related_name='+', null=False)
    _endereco_pagamento = models.OneToOneField('pedido.PedidoVendaEndereco', db_column='pedido_venda_endereco_pagamento_id', related_name='+', null=False)

    tipo = models.ForeignKey('pedido.PedidoVendaTipo', db_column='pedido_venda_tipo_id', related_name='pedidos')
    situacao = models.ForeignKey('pedido.PedidoVendaSituacao', db_column='pedido_venda_situacao_id', related_name='pedidos')
    cliente = models.ForeignKey('cliente.Cliente', related_name='pedidos')
    conta = models.ForeignKey('plataforma.Conta', related_name='pedidos_vendas', on_delete=models.CASCADE)
    contrato = models.ForeignKey('plataforma.Contrato', related_name='pedidos_vendas')
    # cupom = models.ForeignKey("marketing.CupomDesconto", db_column='cupom_desconto_id', related_name='pedidos', null=True)
    envios = models.ManyToManyField('configuracao.Envio', through='PedidoVendaFormaEnvio', related_name='pedidos')
    pagamentos = models.ManyToManyField('configuracao.FormaPagamento', through='PedidoVendaFormaPagamento', related_name='pedidos')

    # A referência e o serviço são usados para identificar que este pedido
    # foi criado por algum serviço externo e depois importado na Loja Integerada
    # ou que ele foi criado na Loja Integrada e depois exportado para outro local.
    referencia = models.TextField(db_column='pedido_venda_referencia', null=True, default=None)

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda"
        verbose_name = u'Pedido Venda'
        verbose_name_plural = u'Pedidos de Venda'
        ordering = ['id']
        unique_together = (("conta", "numero"), )
        get_latest_by = 'id'

    def __unicode__(self):
        return unicode(self.id)

    def criar_endereco(self, tipo, endereco):
        """Cria um endereço para o pedido baseado em um endereço do cliente."""
        # O tipo de endereço só pode ser pagamento ou entrega e o objeto deve
        # ser uma instância do endereço do cliente.
        assert tipo in ['entrega', 'pagamento']
        assert isinstance(endereco, ClienteEndereco)

        campos = ['tipo', 'cpf', 'rg', 'cnpj', 'razao_social', 'ie', 'nome',
                  'endereco', 'numero', 'complemento', 'referencia', 'bairro',
                  'cidade', 'estado', 'cep', 'pais']
        valores = {}
        for campo in campos:
            valores[campo] = getattr(endereco, campo)
            if campo in ['tipo', 'cpf', 'rg', 'cnpj', 'razao_social', 'ie']:
                if not getattr(endereco, campo):
                    valores[campo] = getattr(endereco.cliente.endereco(), campo)

        try:
            novo_endereco = PedidoVendaEndereco.objects.filter(
                conta=self.conta, **valores)[0]
        except IndexError:
            novo_endereco = PedidoVendaEndereco(conta=self.conta)
            for campo, valor in valores.items():
                setattr(novo_endereco, campo, valor)
            novo_endereco.save()
        return novo_endereco

    def _set_endereco_entrega(self, endereco):
        """Ao definir um endereço de entrega é possível definir como um
        endereço do cliente ou como um endereço do pedido.
        """
        if isinstance(endereco, PedidoVendaEndereco):
            self._endereco_entrega = endereco
        elif isinstance(endereco, ClienteEndereco):
            self._endereco_entrega = self.criar_endereco('entrega', endereco)
        else:
            raise TypeError(u'O endereço deve ser do tipo Endereco ou PedidoVendaEndereco. %s foi enviado.' % type(endereco))

    def _get_endereco_entrega(self):
        return self._endereco_entrega

    endereco_entrega = property(_get_endereco_entrega, _set_endereco_entrega)

    def _set_endereco_pagamento(self, endereco):
        """Ao definir um endereço de pagamento é possível definir como um
        endereço do cliente ou como um endereço do pedido.
        """
        if isinstance(endereco, PedidoVendaEndereco):
            self._endereco_pagamento = endereco
        elif isinstance(endereco, ClienteEndereco):
            self._endereco_pagamento = self.criar_endereco('pagamento', endereco)
        else:
            raise TypeError(u'O endereço deve ser do tipo Endereco ou PedidoVendaEndereco. %s foi enviado.' % type(endereco))

    def _get_endereco_pagamento(self):
        return self._endereco_pagamento

    endereco_pagamento = property(_get_endereco_pagamento, _set_endereco_pagamento)

    @property
    def prazo_entrega(self):
        prazo_envio = self.prazo_envio or 0
        entrega = 0
        if self.pedido_envio:
            entrega = self.pedido_envio.prazo or 0
        return prazo_envio + entrega

    @property
    def pedido_envio(self):
        """Retorna a primeira relação de PedidoVendaFormaEnvio do pedido."""
        if not hasattr(self, '_pedido_envio'):
            try:
                self._pedido_envio = self.pedido_envios.all()[0]
            except IndexError:
                self._pedido_envio = None
        return self._pedido_envio

    @property
    def prazo_envio(self):
        """Retorna o maior prazo de envio de todos os itens do pedido."""
        return self.itens.aggregate(prazo=Max('disponibilidade')).get('prazo')

    @property
    def pagamento(self):
        """Retorna a primeira relação de FormaPagamento do pedido."""
        if not hasattr(self, '_pagamento'):
            try:
                self._pagamento = self.pagamentos.all()[0]
            except IndexError:
                self._pagamento = None
        return self._pagamento


class PedidoVendaItem(models.Model):
    """Itens de um pedido de venda.

    Para criar um novo item de venda é preciso enviar produto, produto_pai,
    quantidade, pedido e conta. A partir dos dados do produto os outros campos
    serão preenchidos.
    """
    id = models.AutoField(db_column="pedido_venda_item_id", primary_key=True)
    linha = models.IntegerField(db_column="pedido_venda_item_linha")

    quantidade = models.DecimalField(db_column="pedido_venda_item_quantidade", max_digits=16, decimal_places=3)
    preco_cheio = models.DecimalField(db_column="pedido_venda_item_preco_cheio", max_digits=16, decimal_places=4)
    preco_custo = models.DecimalField(db_column="pedido_venda_item_preco_custo", max_digits=16, decimal_places=4, null=True)
    preco_promocional = models.DecimalField(db_column="pedido_venda_item_preco_promocional", max_digits=16, decimal_places=4, null=True)
    preco_venda = models.DecimalField(db_column="pedido_venda_item_preco_venda", max_digits=16, decimal_places=4)
    preco_subtotal = models.DecimalField(db_column="pedido_venda_item_preco_subtotal", max_digits=16, decimal_places=4)

    tipo = models.CharField(db_column="pedido_venda_item_produto_tipo", max_length=255, null=True)
    sku = models.CharField(db_column="pedido_venda_item_sku", max_length=255)
    nome = models.CharField(db_column="pedido_venda_item_nome", max_length=255)

    # Variação é um campo que armazena um json com os dados de um dicionário de
    # variações do produto, se o produto tem variação: Cor = Azul e Tamanho = P
    # o valor armazenado é: '{"Cor": "Azul", "Tamanho": "P"}'.
    _variacao = models.TextField(db_column="pedido_venda_item_variacao", null=True)
    peso = models.DecimalField(db_column="pedido_venda_item_peso", max_digits=16, decimal_places=3, default=None, null=True)
    altura = models.IntegerField(db_column="pedido_venda_item_altura", default=None, null=True)
    largura = models.IntegerField(db_column="pedido_venda_item_largura", default=None, null=True)
    profundidade = models.IntegerField(db_column="pedido_venda_item_comprimento", default=None, null=True)
    disponibilidade = models.IntegerField(db_column="pedido_venda_item_disponibilidade", null=True)

    pedido = models.ForeignKey('pedido.PedidoVenda', db_column='pedido_venda_id', related_name='itens', on_delete=models.CASCADE)
    pedido_forma_envio = models.ForeignKey('pedido.PedidoVendaFormaEnvio', db_column="pedido_venda_envio_id", related_name='pedido_venda_itens', null=True)
    produto = models.ForeignKey("catalogo.Produto", related_name='pedido_venda_itens', on_delete=models.PROTECT)
    produto_pai = models.ForeignKey("catalogo.Produto", db_column='produto_id_pai', related_name='filhos_pedido_venda_itens', null=True, on_delete=models.PROTECT)
    conta = models.ForeignKey('plataforma.Conta', related_name='pedido_venda_itens')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='pedido_venda_itens')

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_item"
        verbose_name = u'Itens de um pedido de venda'
        verbose_name_plural = u"Itens dos pedidos de vendas"
        ordering = ['id']

    def __unicode__(self):
        return unicode(self.id)

    def reservar_item(self):
        return PedidoVendaItemReserva.objects.create(
            quantidade=self.quantidade,
            pedido=self.pedido,
            pedido_item=self,
            produto=self.produto,
            produto_pai=self.produto_pai,
            conta=self.conta
        )


class PedidoVendaItemReserva(models.Model):
    """Itens reservados de um pedido de venda."""
    id = models.AutoField(db_column="pedido_venda_item_reserva_id", primary_key=True)
    quantidade = models.DecimalField(db_column="pedido_venda_item_reserva_quantidade", max_digits=16, decimal_places=3)

    pedido = models.ForeignKey('pedido.PedidoVenda', db_column='pedido_venda_id', related_name='itens_reservados', on_delete=models.CASCADE)
    pedido_item = models.ForeignKey('pedido.PedidoVendaItem', db_column='pedido_venda_item_id', related_name='itens_reservados')
    produto = models.ForeignKey("catalogo.Produto", related_name='itens_reservados')
    produto_pai = models.ForeignKey("catalogo.Produto", db_column='produto_id_pai', related_name='filhos_itens_reservados', null=True)
    conta = models.ForeignKey('plataforma.Conta', related_name='pedido_venda_itens_reservados')
    contrato = models.ForeignKey('plataforma.Contrato', related_name='pedido_venda_itens_reservados')

    class Meta:
        db_table = u"pedido\".\"tb_pedido_venda_item_reserva"
        verbose_name = u'Itens reservados de um pedido de venda'
        verbose_name_plural = u"Itens reservados dos pedidos de vendas"
        ordering = ['id']
        unique_together = (("conta", "pedido", "pedido_item"), )

    def __unicode__(self):
        return unicode(self.id)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(PedidoVendaItemReserva, self).save(*args, **kwargs)
