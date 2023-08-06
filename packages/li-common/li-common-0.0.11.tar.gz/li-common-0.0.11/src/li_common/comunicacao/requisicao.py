# -*- coding: utf-8 -*-

"""
Componentes para realizar chamadas HTTPs
"""

import json
import urllib
import requests
from requests.exceptions import ConnectionError, Timeout
from li_common import helpers
from li_common.padroes import serializacao


REQUEST_BASE_TIMEOUT = (10, 20)
GRAVA_EVIDENCIA = False


class TipoMetodo(object):
    """
    Enumerador para tipos de métodos HTTP
    """
    get = "get"
    post = "post"
    put = "put"
    delete = "delete"


class Formato(object):
    """
    Enumerador para tipos de formato e o Content-Type equivalente.
    """
    texto = 'text'
    querystring = 'text/html'
    json = 'application/json'
    form_urlencode = 'application/x-www-form-urlencoded'
    xml = 'application/xml'


class Credenciador(object):
    """
    Serviço padrão para construir credenciadores de conexão HTTP para ser usado em li_common.comunicacao.requisicao.Conexao
    """
    class TipoAutenticacao(object):
        """
        Enumerador para tipos de autenticação.
        """
        cabecalho_http = 1
        query_string = 2
        form_urlencode = 3

    def __init__(self, tipo=TipoAutenticacao.cabecalho_http, chave=None):
        self.tipo = tipo
        self.chave = chave or 'Authorization' if tipo == self.TipoAutenticacao.cabecalho_http else 'access_token'

    def define_autenticacao(self):
        """
        Define os dados de autenticação paseado no tipo.
        :return O resultado de ums dos métodos de obtenção de dados de acordo com o tipo de autenticação.
        """
        if self.tipo == self.TipoAutenticacao.cabecalho_http:
            return self.por_cabecalho_http()
        if self.tipo == self.TipoAutenticacao.form_urlencode:
            return self.por_form_urlencoded()
        if self.tipo == self.TipoAutenticacao.query_string:
            return self.por_query_string()
        return None

    def obter_credenciais(self):
        """
        Monta os dados da autenticação
        :return Os valores da autenticação para serem usados por um dos métodos de formatação de acordo com o tipo de autenticação.
        """
        return ''

    def por_query_string(self):
        """
        Formata os dados da autenticação em um par chave=valor
        """
        return "{}={}".format(self.chave, self.obter_credenciais())

    def por_form_urlencoded(self):
        """
        Formata os dados da autenticação em um dicionário
        """
        return {self.chave: self.obter_credenciais()}

    def por_cabecalho_http(self):
        """
        Formata os dados da autenticação em um dicionário
        """
        return {self.chave: self.obter_credenciais()}


class RespostaJsonInvalida(Exception):
    """
    Disparada quando o formato de resposta é definido como JSON porem o conteúdo da resposta não pode ser codificado em JSON.
    """
    pass


class Resposta(object):
    """
    Classe que encapsula os dados de u request.response e já formata o conteúdo em dicionário.
    """
    def __init__(self, request_response, formato_resposta=Formato.json):
        self.sucesso = request_response.status_code in (200, 201)
        self.requisicao_invalida = request_response.status_code == 400
        self.nao_autorizado = request_response.status_code == 401
        self.nao_autenticado = request_response.status_code == 403
        self.nao_encontrado = request_response.status_code == 404
        self.timeout = request_response.status_code == 408
        self.erro_servidor = request_response.status_code == 500
        self.status_code = request_response.status_code
        self.conteudo = {}
        if formato_resposta == Formato.xml:
            self.conteudo = serializacao.Formatador.xml_para_dict(request_response.content)
        if formato_resposta == Formato.json:
            try:
                self.conteudo = json.loads(request_response.content)
            except ValueError:
                self.conteudo = request_response.content
                raise RespostaJsonInvalida(u'O conteudo "{}" não pode ser transformado em JSON.'.format(request_response.content))
        if formato_resposta in (Formato.form_urlencode, Formato.querystring):
            content = urllib.unquote(request_response.content).decode('utf8')
            self.conteudo = {par.split("=")[0].lower(): par.split("=")[1].lower() for par in content.split("&")}
        if formato_resposta == Formato.texto:
            self.conteudo = request_response.content


class Conexao(object):
    """
    Componente para realizar a conexão HTTP.
    """
    def __init__(self, formato_envio=Formato.json, formato_resposta=Formato.json, headers=None, credenciador=None):
        self.headers = {'Content-Type': '{}; charset=ISO-8859-1'.format(formato_envio)}
        self.formato_envio = formato_envio
        self.formato_resposta = formato_resposta
        self.credenciador = credenciador
        if headers:
            self.headers.update(headers)
        self.dados_envio = {}

    def define_url_com_autenticacao(self, url):
        """
        Define a autenticação a ser usada.
        Se for do tipo cabeçalho http, adiciona o resultado do credenciador no header.
        Se for do tipo form urlencode, adiciona o resultado do credenciador nos dados a serem enviados.
        Se for do tipo query string, adiciona o resultado do credenciador na url passada.
        :param url: A url que será chamada, onde a autenticação será adicionada caso o tipo de envio seja por query string.
        :type url: str
        :return: A url formatada
        :rtype: str
        """
        autenticacao = self.credenciador.define_autenticacao()
        if self.credenciador.tipo == Credenciador.TipoAutenticacao.cabecalho_http:
            self.headers.update(autenticacao)
        if self.credenciador.tipo == Credenciador.TipoAutenticacao.form_urlencode:
            self.dados_envio.update(autenticacao)
        if self.credenciador.tipo == Credenciador.TipoAutenticacao.query_string:
            separador = "&" if "?" in url else "?"
            return "{}{}{}".format(url, separador, autenticacao)
        return url

    @helpers.tente_outra_vez((ConnectionError, Timeout), tentativas=3, tempo_espera=4)
    def faz_request(self, url, metodo=TipoMetodo.get):
        """
        Executa o método HTTP especificado na url
        :param url: A url onde será feita a chamada.
        :type url: str
        :param metodo: Um dos métodos HTTP disponíveis
        :type metodo: str
        :return: Um objeto Resposta com os dados retornados pelo request.response.
        :rtype: Resposta
        """
        if self.credenciador:
            url = self.define_url_com_autenticacao(url)
        if self.formato_envio == Formato.querystring:
            resposta = getattr(requests, metodo)(url, params=self.dados_envio, headers=self.headers, timeout=REQUEST_BASE_TIMEOUT)
        elif self.formato_envio == Formato.form_urlencode:
            resposta = getattr(requests, metodo)(url, data=self.dados_envio, headers=self.headers, timeout=REQUEST_BASE_TIMEOUT)
        elif self.formato_envio == Formato.xml:
            dados = self.dados_envio.get('dados', '')
            resposta = getattr(requests, metodo)(url, data=dados, headers=self.headers, timeout=REQUEST_BASE_TIMEOUT)
        else:
            dados_envio = self.dados_envio
            if type(self.dados_envio is dict):
                dados_envio = json.dumps(self.dados_envio)
            resposta = getattr(requests, metodo)(url, data=dados_envio, headers=self.headers, timeout=REQUEST_BASE_TIMEOUT)
        return Resposta(resposta, formato_resposta=self.formato_resposta)

    def prepara_request(self, url, metodo=TipoMetodo.get, dados=None):
        """
        Método de preparação para o request.
        :param url: A url onde será feita a chamada.
        :type url: str
        :param metodo: Um dos métodos HTTP disponíveis
        :type metodo: str
        :param dados: Dados a serem passados para o request.
        :type dados: dict or str
        :return: Um objeto Resposta com os dados retornados pelo request.response.
        :rtype: Resposta
        """
        if dados:
            if isinstance(dados, dict):
                self.dados_envio.update(dados)
            else:
                self.dados_envio["dados"] = dados
        resposta = self.faz_request(url, metodo)
        return resposta

    def get(self, url, dados=None):
        """
        Realiza uma chamada GET na url com os dados passados
        :param url: A url onde será feita a chamada.
        :type url: str
        :param dados: Dados a serem passados para o request.
        :type dados: dict or str
        :return: Um objeto Resposta com os dados retornados pelo request.response.
        :rtype: Resposta
        """
        return self.prepara_request(url, TipoMetodo.get, dados)

    def post(self, url, dados=None):
        """
        Realiza uma chamada POST na url com os dados passados
        :param url: A url onde será feita a chamada.
        :type url: str
        :param dados: Dados a serem passados para o request.
        :type dados: dict or str
        :return: Um objeto Resposta com os dados retornados pelo request.response.
        :rtype: Resposta
        """
        return self.prepara_request(url, TipoMetodo.post, dados)

    def put(self, url, dados=None):
        """
        Realiza uma chamada PUT na url com os dados passados
        :param url: A url onde será feita a chamada.
        :type url: str
        :param dados: Dados a serem passados para o request.
        :type dados: dict or str
        :return: Um objeto Resposta com os dados retornados pelo request.response.
        :rtype: Resposta
        """
        return self.prepara_request(url, TipoMetodo.put, dados)

    def delete(self, url, dados=None):
        """
        Realiza uma chamada DELETE na url com os dados passados
        :param url: A url onde será feita a chamada.
        :type url: str
        :param dados: Dados a serem passados para o request.
        :type dados: dict or str
        :return: Um objeto Resposta com os dados retornados pelo request.response.
        :rtype: Resposta
        """
        return self.prepara_request(url, TipoMetodo.delete, dados)
