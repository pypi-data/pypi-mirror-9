# -*- coding: utf-8 -*-

"""
Módulo contendo a base para todas as entidades usadas nos projetos da Loja Integrada.
"""

from decimal import Decimal
from li_common.padroes import extensibilidade, serializacao


class Entidade(object):
    """
    Classe base para as Entidades simples. Ela fornece serialização padrão como dicionário ou xml.
    """
    formatador = serializacao.Formatador
    _chaves_alternativas_para_serializacao = {}
    _parametros_para_serializacao = {}
    _nao_serializar = []

    def remove_atributo_da_serializacao(self, atributo):
        """
        Inclui um atributo na lista para não ser serializado
        :param atributo: O nome do atributo a ser incluido na lista de não serialização
        :type atributo: str
        :return: None
        """
        self._nao_serializar.append(atributo)

    def _membro_nao_eh_serializavel(self, atributo):
        """
        Alguns membros não podem sair na serialização. Esse método verifica isso e retorna True caso o atributo ou propriedade
        não possa ser serializado.
        :param membro: Tupla contendo nome, valor do membro a ser testado
        :type membro: tuple
        :return: True caso o membro não possa ser serializado.
        :rtype: bool
        """
        if atributo == 'formatador':
            return True
        if atributo.startswith('_'):
            return True
        if atributo in self._nao_serializar:
            return True
        if hasattr(getattr(self, atributo), '__call__'):
            return True
        return False

    def _extrai_membros(self):
        """
        Usa retorna todos os membros da classe que podem ser serializados
        :return: lista contendo tuplas com nome, valor do membro.
        :rtype: list
        """
        for atributo in dir(self):
            if self._membro_nao_eh_serializavel(atributo):
                continue
            yield atributo, getattr(self, atributo)

    def _processa_valor_atributo(self, valor, metodo, formato=None, **argumentos_metodo):
        """
        Processa o valor do atributo na serialização para o caso dele ser uma instância de Entidade.
        :param valor: É o valor do atributo.
        :param metodo: O nome do método de serialização, podendo ser 'to_dict' ou 'to_xml'.
        :type metodo: str
        :param formato: Caso o valor precise ser formatado, passe a string de formatação (str.format()) nesse parâmetro.
        :type formato: str
        :param argumentos_metodo: kwargs a ser passado para o método de serialização.
        :return: Retorna o valor do atributo processado.
        :rtype: object
        """
        if issubclass(valor.__class__, Entidade):
            return getattr(valor, metodo)(**argumentos_metodo)
        if isinstance(valor, unicode):
            valor = valor.encode('utf-8')
        if isinstance(valor, Decimal):
            valor = self.formatador.formata_decimal(valor, como_float=True)
        if formato:
            return formato.format(valor)
        return valor

    @property
    def _chave_serializacao(self):
        """
        Retorna a chave para ser usada na serialização como chave de dicionário ou elemento do xml para a Entidade.
        Usa o Entidade._chaves_alternativas_para_serializacao para retornar a chave alternativa, se for o caso ou o nome da classe.
        :return: A chave que será usada na serialização
        :rtype: str
        """
        if 'self' in self._chaves_alternativas_para_serializacao:
            return self._chaves_alternativas_para_serializacao['self']
        return self.__class__.__name__

    def _chave_atributo(self, atributo):
        """
        Retorna a chave para ser usada na serialização como chave de dicionário ou elemento do xml para o atributo passado.
        Usa o Entidade._chaves_alternativas_para_serializacao para retornar a chave alternativa, se for o caso ou o nome do atributo.
        :param atributo: O nome do atributo para o qual retornar a chave.
        :return: A chave que será usada na serialização
        :rtype: str
        """
        if atributo in self._chaves_alternativas_para_serializacao:
            atributo = self._chaves_alternativas_para_serializacao[atributo]
        return atributo

    def _membro_to_dict(self, atributo, valor):
        """
        Serializa um membro da classe em dicionário
        :param atributo: Nome do atributo a ser convertido
        :type atributo: str
        :param valor: Valor do atributo.
        :type valor: object
        :return: O atributo serializado em {atributo: valor}
        :rtype: dict
        """
        valor = self._processa_valor_atributo(valor, 'to_dict')
        if isinstance(valor, list) and valor:
            valor = [self._processa_valor_atributo(valor, 'to_dict') for valor in valor]
        return {self._chave_atributo(atributo): valor}

    def to_dict(self):
        """
        Serializa os atributos e propriedades públicos da entidade em dicionário
        :return: A entidade como um dicionário
        :rtype: dict
        """
        retorno = {}
        for atributo, valor in self._extrai_membros():
            retorno.update(self._membro_to_dict(atributo, valor))
        return retorno

    def _monta_parametros(self, chave):
        """
        Monta os parâmetros de xml (chave="valor") para a serialização
        :param chave: A chave do parâmetro. Os valores estão definidos no atributo Entidade._parametros_para_serializacao e deve ser um dict
        :type chave: str
        :return: O par nome-valor dos formatos como nome1="valor1" nome2="valor2"
        :rtype: str
        """
        parametros = []
        for parametro in self._parametros_para_serializacao[chave]:
            valor_parametro = self._parametros_para_serializacao[chave][parametro]
            if isinstance(valor_parametro, unicode):
                valor_parametro = valor_parametro.encode('utf-8')
            parametros.append('{}="{}"'.format(parametro, valor_parametro))
        return ' '.join(parametros)

    def _membro_to_xml(self, atributo, valor):
        """
        Serializa um membro da classe em xml
        :param atributo: Nome do atributo a ser convertido
        :type atributo: str
        :param valor: Valor do atributo.
        :type valor: object
        :return: O atributo serializado em <atributo>valor</atributo> ou <atributo param1="valor-param1" param2="valor-param2">valor</atributo>
        :rtype: str
        """
        valor = self._processa_valor_atributo(valor, 'to_xml')
        if isinstance(valor, list) and valor:
            lista = []
            for valor_na_lista in valor:
                lista.append(self._processa_valor_atributo(valor_na_lista, 'to_xml', formato='<item>{}</item>', raiz=True))
            valor = ''.join(lista)
        atributo = self._chave_atributo(atributo)
        if atributo in self._parametros_para_serializacao:
            return '<{} {}>{}</{}>'.format(atributo, self._monta_parametros(atributo), valor, atributo)
        return '<{}>{}</{}>'.format(atributo, valor, atributo)

    def to_xml(self, raiz=False):
        """
        Serializa os atributos e propriedades públicos da entidade em xml
        :return: String contendo a entidade em formato de xml.
        :rtype: str
        """
        retorno = []
        if raiz:
            if 'self' in self._parametros_para_serializacao:
                retorno.append('<{} {}>'.format(self._chave_serializacao, self._monta_parametros('self')))
            else:
                retorno.append('<{}>'.format(self._chave_serializacao))
        for atributo, valor in self._extrai_membros():
            retorno.append(self._membro_to_xml(atributo, valor))
        if raiz:
            retorno.append('</{}>'.format(self._chave_serializacao))
        return ''.join(retorno)

    @classmethod
    def criar_apartir_de(cls, dados):
        """
        Retorna uma instância da entidade baseado em um dicionário
        :param dados: Os dados para preencher a entidade.
        :type dados: dict
        :return: Uma instância da entidade
        :rtype: li_common.padroes.entidades.Entidade
        """
        entidade = cls()
        for dado in dados:
            if hasattr(entidade, dado):
                valor_padrao = getattr(entidade, dado, None)
                valor = dados[dado] or valor_padrao
                setattr(entidade, dado, valor)
        return entidade

    def preencher_com(self, dados, campos=None, soh_atributo=False):
        """
        Preenche os atributos de uma entidade com os dados passados
        :param dados: Os dados em forma de dicionário. As chaves devem ser os nomes de atributos da entidade.
        :type dados: dict
        :param campos: Lista com nomes de atributos a serem considerados
        :type campos: list
        :return: None
        """
        if not campos:
            campos = dados.keys()
        for campo in campos:
            if soh_atributo and not hasattr(self, campo):
                continue
            valor_padrao = getattr(self, campo, None)
            valor = dados.get(campo, None) or valor_padrao
            setattr(self, campo, valor)


class EntidadeExtensivel(Entidade, extensibilidade.Extensao):
    """
    Fornece funcionalidade para que uma entidade possa usar a extensibilidade ao instanciar outras entidades.
    """
    pass
