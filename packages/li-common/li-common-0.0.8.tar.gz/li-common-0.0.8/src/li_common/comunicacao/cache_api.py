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
        self.regras_sem_cache = {}

    def define_cache(self, url, max_age=0, sem_cache=None):
        """
        Define os dados de cache para uma URL
        :param url: A URL para qual o cache será definido
        :type url: str
        :param max_age: O tempo de vida, em segundos, do cache
        :type max_age: int
        :param sem_cache: Dicionário para definição de regras para que o cache não seja aplicado. Ex: sem_cache={'querystring': 'no-cache=1'} define que
        quando a url for chamada com uma querystring contendo no-cache=1, o cache não será aplicado.
        :type sem_cache: dict
        :return: A url para ser usada na definição da rota
        :rtype: str
        """
        self.definicoes[url] = {
            'max_age': max_age
        }
        if sem_cache is not None:
            self.regras_sem_cache[url] = sem_cache
        return url

    def aplica_cache(self, request, headers, **excecoes):
        """
        Aplica um cache na URL que doi acessada
        :param request: O objeto request da requisição Flask
        :type request: flask.request
        :param headers: Um dicionário onde a chave Cache-Control será adicionada
        :type headers: dict
        :param excecoes: Parâmetros que podem definir exceções à aplicação de cache. Caso um parâmetro seja passado no modo param=False e o
        mesmo parâmetro tenha sido registrado no DefinicaoDeCache.define_cache, o cache não será aplicado
        :type excecoes: kwargs
        :return: None
        """
        url = request.url_rule.rule
        if url in self.definicoes:
            max_age = self.definicoes[url]['max_age']
            regra = self.regras_sem_cache.get(url, {})
            if regra:
                querystring = regra.get('querystring', None)
                if querystring and querystring in request.query_string:
                    max_age = 0
                parametro = regra.get('parametro', '')
                excecao = excecoes.get(parametro, False)
                if excecao:
                    max_age = 0
            headers['Cache-Control'] = "max-age={}".format(max_age)
