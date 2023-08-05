# -*- coding: utf-8 -*-
from django.db import models


class Pais(models.Model):
    """Países."""
    id = models.CharField(db_column="pais_id", max_length=3, primary_key=True)
    nome = models.CharField(db_column="pais_nome", max_length=64)
    numero = models.CharField(db_column="pais_numero", max_length=3)
    codigo = models.CharField(db_column="pais_codigo", max_length=2, unique=True)

    class Meta:
        app_label = "public"
        db_table = u"public\".\"tb_pais"

    # def __unicode__(self):
    #     return self.nome


class Estado(models.Model):

    """Estados."""
    id = models.AutoField(db_column="estado_id", primary_key=True)
    uf_id = models.IntegerField(db_column="uf_id", unique=True)
    nome = models.CharField(db_column="estado_nome", max_length=100)
    uf = models.CharField(db_column="estado_uf", max_length=2)

    pais = models.ForeignKey('public.Pais', db_column="pais_id")

    class Meta:
        app_label = "public"
        db_table = u"public\".\"tb_estado"

    # def __unicode__(self):
    #     return self.nome


class Cidade(models.Model):

    """Cidades."""
    id = models.AutoField(db_column="cidade_id", primary_key=True)
    cidade = models.CharField(db_column="cidade", max_length=100)
    cidade_alt = models.CharField(db_column="cidade_alt", max_length=100)
    uf = models.CharField(db_column="uf", max_length=2)
    uf_munic = models.IntegerField(db_column="uf_munic")
    munic = models.IntegerField(db_column="munic")

    estado = models.ForeignKey('public.Estado', db_column="uf_id")

    class Meta:
        db_table = u"public\".\"tb_cidade"

    # def __unicode__(self):
    #     return self.nome
