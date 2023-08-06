# -*- coding: utf-8 -*-

"""
Módulo contendo a base para todos os serviços usados nos projetos da Loja Integrada.
"""
from importlib import import_module
from li_common.comunicacao import requisicao
from li_common.padroes import extensibilidade, serializacao


class EntidadeNaoEncontrada(Exception):
    """
    Disparada quando a entidade passada não for encontrada no modulo.
    """
    pass


class ParamentrosDeEntidadeInvalidos(Exception):
    """
    Disparada quando o init da classe não aceita os parâmetros passados.
    """
    pass


class Servico(extensibilidade.Extensao):
    """
    Classe base para os serviços. Já define a extensibilidade do serviço.
    """
    formatador = serializacao.Formatador

    @classmethod
    def cria_entidade(cls, nome_modulo, entidade, **kwargs):
        """
        Factory para instancias de entidades. Use esse método para evitar import circular entre os módulos de servicos e entidades
        :param nome_modulo: Nome completo do módulo onde está a entidade. Ex.: pagador.entidades
        :type nome_modulo: str
        :param entidade: Nome da classe da entidade.
        :type entidade: str
        :param kwargs: Argumentos que devem ser passados para o init da classe.
        :type kwargs: dict
        :return: A instância da classe.
        """
        modulo = import_module('{}.entidades'.format(nome_modulo))
        try:
            classe = getattr(modulo, entidade)
        except AttributeError, ex:
            raise EntidadeNaoEncontrada(u'Não foi encontrado a classe "{}.entidades.{}" no ambiente. {}'.format(nome_modulo, entidade, ex))
        try:
            return classe(**kwargs)
        except TypeError:
            raise ParamentrosDeEntidadeInvalidos(u'A classe "{}.entidades.{}" não aceitou os argumentos passados: "{}".'.format(nome_modulo, entidade, kwargs))

    @classmethod
    def obter_conexao(cls, formato_envio=requisicao.Formato.json, formato_resposta=requisicao.Formato.json, headers=None):
        """
        Factory para criação de objeto conexão para realizar chamadas HTTP.
        :param formato_envio: Qual o formato que os dados deverão ser passados nas chamadas HTTP da conexão.
        :type formato_envio: li_common.comunicacao.requisicao.Formato
        :param formato_resposta: Qual o formato que os dados serão respondido nas chamadas HTTP da conexão.
        :type formato_resposta: li_common.comunicacao.requisicao.Formato
        :param headers: O cabeçalho HTTP a ser enviado na chamada.
        :type headers: dict
        :return: Uma instância de li_common.comunicacao.requisicao.Conexao
        :rtype: li_common.comunicacao.requisicao.Conexao
        """
        return requisicao.Conexao(formato_envio=formato_envio, formato_resposta=formato_resposta, headers=headers)
