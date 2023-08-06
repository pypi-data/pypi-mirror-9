# -*- coding: utf-8 -*-

"""
Componentes para a criação de recursos para serem usados nas APIs Rest
"""
from flask import make_response, request
import flask_restful
from werkzeug import exceptions

from li_common.padroes import serializacao


class RecursoBase(flask_restful.Resource):
    """
    Representa um recurso base de api rest
    """
    app = None

    def __init__(self):
        self._dados = {}

    @property
    def dados(self):
        """
        Obtem os dados enviados em um request, analisando args, form e json e adicionando todos em um dicionário único
        :return: Um dicionário com os valores dos dados passados no request
        :rtype: dict
        """
        if not self._dados:
            self._dados = {}
            for arg in request.args:
                self._dados[arg] = request.args[arg]
            for arg in request.form:
                self._dados[arg] = request.form[arg]
            try:
                self._dados.update(request.get_json())
            except (TypeError, exceptions.BadRequest):
                pass
        return self._dados

    @classmethod
    def resposta(cls, conteudo, status=200, excecao=None):
        """
        Gera um objeto response do Flask com um conteúdo padronizado para todos os tipos de retorno
        :param conteudo: O conteudo a ser inserido no padrão de resposta. Pode ser um dict ou uma str
        :type conteudo: dict, str
        :param status: Status Code para a resposta. Padrão é 200
        :type status: int
        :param excecao: Caso a resposta seja 500, qual a exceção que gerou o erro 500.
        :type excecao: Exception
        :return: Um objeto response do Flask
        """
        conteudo, status = serializacao.ResultadoDeApi.resposta(conteudo, cls.app.nome_api, cls.app.version, status, excecao)
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        cls.app.cache.aplica_cache(request, headers)
        return make_response(conteudo, status, headers)
