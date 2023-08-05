# -*- coding: utf-8 -*-

"""
Módulo que oferece funcionalidades para permitir a definição e aplicação de cache em URLs de APIs Flask
"""


def definicao(nome_api=None):
    """
    Método construtor para que uma app inicialize um cache sem o risco de misturar com outra app
    :param nome_api: O nome da api
    :type nome_api: str
    :return: Um objeto para montar as definições de cache
    :rtype cache_api.DefinicaoDeCache
    """
    return DefinicaoDeCache(nome_api)


class DefinicaoDeCache(object):
    """
    Classe que define os caches e permite aplica-los no cabeçalho http Cache-Control da reposta
    """

    def __init__(self, nome_api=None):
        self.nome_api = nome_api
        self.definicoes = {}

    def define_cache(self, url, max_age=0):
        """
        Define os dados de cache para uma URL
        :param url: A URL para qual o cache será definido
        :type url: str
        :param max_age: O tempo de vida, em segundos, do cache
        :type max_age: int
        :return: A url para ser usada na definição da rota
        :rtype: str
        """
        self.definicoes[url] = {
            'max_age': max_age
        }
        return url

    def aplica_cache(self, request, headers):
        """
        Aplica um cache na URL que doi acessada
        :param request: O objeto request da requisição Flask
        :type request: flask.request
        :param headers: Um dicionário onde a chave Cache-Control será adicionada
        :type headers: dict
        :return: None
        """
        url = request.url_rule.rule
        if url in self.definicoes:
            headers['Cache-Control'] = "max-age={}".format(self.definicoes[url]['max_age'])
