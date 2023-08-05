# -*- coding: utf-8 -*-

from django.db import models


class CobrancaItem(models.Model):
    """Item de cobrança."""
    id = models.AutoField(db_column="cobranca_item_id", primary_key=True)
    referencia_tabela = models.CharField(db_column="cobranca_item_referencia_tabela", max_length=64, null=True, default=None)
    referencia_linha_id = models.BigIntegerField(db_column="cobranca_item_referencia_linha_id", null=True, default=None)
    referencia_situacao = models.CharField(db_column="cobranca_item_referencia_situacao", null=True, max_length=12, default=None)
    conta_id = models.IntegerField(db_column="conta_id", null=True, default=None)

    class Meta:
        db_table = u"cobranca\".\"tb_cobranca_item"

